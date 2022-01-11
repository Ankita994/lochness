import os
import string
import smtplib
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from datetime import date
from typing import List
import getpass
import socket
import subprocess

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
                       second_message: str, code: List[str]) -> None:
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
    msg['Subject'] = f'Lochness update {date.today()}'
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(sender, sender_pw)
    s.sendmail(sender, recipients, msg.as_string())
    s.quit()


def send_out_daily_updates(Lochness):
    '''Send daily updates from Lochness'''
    command = f"tree {Lochness['phoenix_root']} -L 3"  # the shell command
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=True)
    output, _ = process.communicate()
    list_of_lines_from_tree = output.decode("utf-8").split('\n')

    list_of_datatypes_and_subject_updated = ['a', 'b']

    print(output.decode("utf-8"))
    send_detail_google(
        Lochness,
        'Lochness', f'Daily updates {date.today}',
        'List of data types updated today',
        list_of_datatypes_and_subject_updated,
        list_of_lines_from_tree)


def attempts_error(Lochness, attempt):
    msg = '\n'.join(attempt.warnings)
    send(Lochness['admins'], Lochness['sender'], 'error report', msg)


def metadata_error(Lochness, message):
    send(Lochness['admins'], Lochness['sender'], 'bad metadata', message)

