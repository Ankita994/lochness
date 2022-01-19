import os
from pathlib import Path
import string
import smtplib
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, date, timedelta
from typing import List
import getpass
import subprocess
import pandas as pd
from pytz import timezone
tz = timezone('EST')

__dir__ = os.path.dirname(__file__)

def send(recipients, sender, subject, message):
    '''send an email'''
    email_template = os.path.join(__dir__, 'template.html')
    with open(email_template, 'r') as fo:
        template = string.Template(fo.read())
    message = template.safe_substitute(message=str(message))
    msg = MIMEText(message, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    s = smtplib.SMTP('localhost')
    s.sendmail(sender, recipients, msg.as_string())
    s.quit()


def send_detail_google(Lochness,
                       title: str, subtitle: str, first_message: str,
                       second_message: str, code: List[str],
                       in_mail_footer: str,
                       test: bool = False) -> None:
    '''Send email using a Gmail account with "Less secure app access" turned on

    Set up a Google account to send out emails using Google's SMTP server. You need
    to turn on "Less secure app access" from "Manage your Google account" page 
    in order to use this feature.

    The configuration file should have

        sender: senderemail@gmail.com
        notify:
          __global__:
              - receiver1@anyemail.com
              - receiver2@anyemail.com

    The keyring file should have email password at the same level as the
    "SECRETS" field.

        {...,
        "SECRETS": {"PronetLA": "LOCHNESS_SECRETS"},
        "email_sender_pw": "PASSWORD"
        }
    '''

    sender = Lochness['sender']
    sender_pw = Lochness['keyring']['lochness']['email_sender_pw']
    recipients_for_each_study = Lochness['notify']

    recipients = []
    for study, study_recipients in recipients_for_each_study.items():
        for recipient in study_recipients:
            if recipients not in recipients:
                recipients.append(recipient)

    email_template_dir = os.path.join(__dir__)
    env = Environment(loader=FileSystemLoader(str(email_template_dir)))
    template = env.get_template('bootdey_template.html')
    footer = 'If you see any error, please email kevincho@bwh.harvard.edu'

    server_name = Lochness['project_name'] \
        if 'project_name' in Lochness else 'Data aggregate server'
    title = f'{server_name}: {title}'

    html_str = template.render(title=title,
                               subtitle=subtitle,
                               first_message=first_message,
                               second_message=second_message,
                               code=code,
                               in_mail_footer=in_mail_footer,
                               footer=footer,
                               server=server_name,
                               username=getpass.getuser())

    msg = MIMEText(html_str, 'html')
    msg['Subject'] = f'Lochness update {datetime.now(tz).date()}'
    msg['From'] = sender
    msg['To'] = recipients[0]
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(sender, sender_pw)
    if not test:
        s.sendmail(sender, recipients, msg.as_string())
        print('Email sent')
    else:
        print(html_str)

    s.quit()


def send_out_daily_updates(Lochness, days: int = 1, test: bool = False):
    '''Send daily updates from Lochness'''

    s3_log = Path(Lochness['phoenix_root']) / 's3_log.csv'
    if s3_log.is_file():
        s3_df = pd.read_csv(s3_log)
        s3_df['timestamp'] = pd.to_datetime(s3_df['timestamp'])
        s3_df['ctime'] = pd.to_datetime(s3_df['ctime']).apply(
                lambda x: x.replace(microsecond=0))

        # get the timestamp to check the dataflow from
        date_to_check_from = datetime.now(tz).date() - timedelta(days=days-1)
        timestamp_to_check_from = pd.Timestamp(date_to_check_from)

        s3_df_selected = s3_df[s3_df['timestamp'] > timestamp_to_check_from]

        s3_df_selected = s3_df_selected.fillna('_')

        s3_df_selected = s3_df_selected[~s3_df_selected.filename.str.contains(
            'metadata.csv')][['timestamp', 'filename', 'protected', 'study',
                              'processed', 'subject', 'datatypes', 'ctime']]

        s3_df_selected['date'] = s3_df_selected['timestamp'].apply(
                lambda x: x.date())
        count_df = s3_df_selected.groupby([
            'date', 'protected', 'study',
            'processed', 'subject', 'datatypes']).count()[['filename']]
        count_df.columns = ['file count']
        count_df = count_df.reset_index()
        s3_df_selected.drop('date', axis=1, inplace=True)

    else:
        s3_df_selected = pd.DataFrame()
        count_df = pd.DataFrame()

    list_of_lines_from_tree = ['']

    day_days = 'days' if days > 1 else 'day'

    if len(s3_df_selected) == 0:
        send_detail_google(
            Lochness,
            'Lochness', f'Daily updates {datetime.now(tz).date()}',
            'There is no update!', '',
            list_of_lines_from_tree,
            '',
            test)
    else:
        s3_df_selected.columns = ['Transfer time (UTC)', 'File name',
                                  'Protected', 'Study', 'Processed', 'Subject',
                                  'Datatype', 'Download time (UTC)']
        s3_df_selected.reset_index().drop('index', axis=1, inplace=True)
        in_mail_footer = 'Note that only S3 transferred files are included.'

        send_detail_google(
            Lochness,
            'Lochness', f'Daily updates {datetime.now(tz).date()} '
                        f'(for the past {days} {day_days})',
            'Summary of files sent to NDA' + count_df.to_html(),
            'Each file in detail' + s3_df_selected.to_html(),
            list_of_lines_from_tree,
            in_mail_footer,
            test)


def attempts_error(Lochness, attempt):
    msg = '\n'.join(attempt.warnings)
    send(Lochness['admins'], Lochness['sender'], 'error report', msg)


def metadata_error(Lochness, message):
    send(Lochness['admins'], Lochness['sender'], 'bad metadata', message)

