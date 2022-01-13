#!/usr/bin/env python
import sys
import lochness
from pathlib import Path
import argparse as ap
import lochness.config as config
from lochness.email import send_out_daily_updates
from lochness.transfer import create_s3_transfer_table


def parse_args(argv):
    parser = ap.ArgumentParser(description='PHOENIX data syncer')
    parser.add_argument('-c', '--config', required=True,
                        help='Configuration file')
    parser.add_argument('-d', '--days', type=int,
                        help='Number of days to summarize dataflow')
    parser.add_argument('-rd', '--recreate_db', action='store_true',
                        help='Recreate s3_log database based on the log file')
    parser.add_argument('-l', '--log_file', help='Log file, only used when '
                        '--recreate_db option is used')

    args = parser.parse_args(argv)
    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    Lochness = config.load(args.config)

    if args.log_file:
        Lochness['log_file'] = str(args.log_file)
    else:
        Lochness['log_file'] = Path(Lochness['phoenix_root']).parent / \
                'log.txt'

    if args.recreate_db:
        if not Path(Lochness['log_file']).is_file():
            sys.exit('No log_file')
        else:
            create_s3_transfer_table(Lochness, True)
    else:
        create_s3_transfer_table(Lochness)

    send_out_daily_updates(Lochness, args.days)
