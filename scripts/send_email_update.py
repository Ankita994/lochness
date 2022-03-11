#!/usr/bin/env python
import sys
import lochness
from pathlib import Path
import argparse as ap
import lochness.config as config
from lochness.email import send_out_daily_updates
from lochness.transfer import create_s3_transfer_table
from lochness.utils.source_check import check_source
from typing import List

def parse_args(argv):
    parser = ap.ArgumentParser(description='PHOENIX data syncer')
    parser.add_argument('-c', '--config', required=True,
                        help='Configuration file')
    parser.add_argument('-d', '--days', type=int, default=1,
                        help='Number of days to summarize dataflow')
    parser.add_argument('-rd', '--recreate_db', action='store_true',
                        help='Recreate s3_log database based on the log file')
    parser.add_argument('-l', '--log_file', default=False,
                        help='Log file, only used when --recreate_db option '
                             'is used')
    parser.add_argument('-r', '--recipients', nargs='+', type=str,
                        default=False,
                        help='List of recipients - with this option the '
                             'recipients in the config file will be ignored')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Dry run of email functionality')

    args = parser.parse_args(argv)
    return args


def send_email_update(config_file: str, days: int, recreate_db: bool,
                      log_file: str, recipients: List[str],
                      test: bool) -> None:
    '''Send email update of previous s3 data sync

    Key arguments:
        config_file: location of Lochness configuration file, str.
        days: number of days from today, to summarize the dataflow for, int.
        recreate_db: True if s3_log.csv needs to be recreated based on the
                     log_file given, bool.
        log_file: location of lochness sync.py log file, str.
        recipients: list of email addresses to send out the summary to, list.

    Note:
        configuration file requires keyring_file, sender, and notify field.
        The keyring_file field should direct to an encrypted keyring file, with
        email_sender_pw (the password for "sender") which is used to log in to
        the smtp server.

        When s3_log.csv is required to be recreated, by using recreate_db=True,
        a log_file should also be provided and this pipeline requires shell
        output lines from s3 transfer to be present in this log file.
    '''

    Lochness = config.load(config_file)

    # update recipients
    if recipients:
        Lochness['notify'] = {'_': recipients}
        Lochness['file_check_notify'] = {'_': recipients}


    if log_file:
        Lochness['log_file'] = str(log_file)
    else:
        Lochness['log_file'] = Path(Lochness['phoenix_root']).parent / \
                'log.txt'

    if recreate_db:
        if not Path(Lochness['log_file']).is_file():
            sys.exit('No log_file')
        else:
            create_s3_transfer_table(Lochness, True)
    else:
        create_s3_transfer_table(Lochness)

    send_out_daily_updates(Lochness, days, test)
    check_source(Lochness)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    send_email_update(args.config, args.days, args.recreate_db,
                      args.log_file, args.recipients, args.test)
