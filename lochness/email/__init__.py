import os
from pathlib import Path
import string
import smtplib
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, date, timedelta
from typing import List
import getpass
import socket
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
                       test: bool = False) -> None:
    '''Send email using gmail account which has it's "Less secure app" allowed

    Set up an google account to send out emails using its SMTP server. You need
    to allow "Less secure app" in Google aacount page in order to use this
    function.

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
    html_str = template.render(title=title,
                               subtitle=subtitle,
                               first_message=first_message,
                               second_message=second_message,
                               code=code,
                               footer=footer,
                               server=socket.gethostname(),
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


def send_out_daily_updates(Lochness, test: bool = False):
    '''Send daily updates from Lochness'''

    s3_log = Path(Lochness['phoenix_root']) / 's3_log.csv'
    if s3_log.is_file():
        s3_df = pd.read_csv(s3_log)
        s3_df['timestamp'] = pd.to_datetime(s3_df['timestamp'])

        s3_df_today = s3_df[s3_df['timestamp'] > pd.Timestamp(datetime.now(tz).date())]

        s3_df_today = s3_df_today.fillna('_')

        s3_df_today = s3_df_today[~s3_df_today.filename.str.contains(
            'metadata.csv')][['timestamp', 'filename', 'protected', 'study',
                              'processed', 'subject', 'datatypes']]

        s3_df_today['date'] = s3_df_today['timestamp'].apply(
                lambda x: x.date())
        count_df = s3_df_today.groupby(['date', 'protected', 'study',
                'processed', 'subject', 'datatypes']).count()[['filename']]
        count_df.columns = ['file count']
        count_df = count_df.reset_index()
        s3_df_today.drop('date', axis=1, inplace=True)

    else:
        s3_df_today = pd.DataFrame()
        count_df = pd.DataFrame()

    list_of_lines_from_tree = ['']

    if len(s3_df_today) == 0:
        send_detail_google(
            Lochness,
            'Lochness', f'Daily updates {datetime.now(tz).date()}',
            'There is no update today!', '',
            list_of_lines_from_tree,
            test)
    else:
        send_detail_google(
            Lochness,
            'Lochness', f'Daily updates {datetime.now(tz).date()}',
            'Summary of files sent to NDA today' + count_df.to_html(),
            'Each file in detail' + s3_df_today.to_html(),
            list_of_lines_from_tree,
            test)


def attempts_error(Lochness, attempt):
    msg = '\n'.join(attempt.warnings)
    send(Lochness['admins'], Lochness['sender'], 'error report', msg)


def metadata_error(Lochness, message):
    send(Lochness['admins'], Lochness['sender'], 'bad metadata', message)

