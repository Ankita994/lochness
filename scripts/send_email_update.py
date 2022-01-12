#!/usr/bin/env python
import sys
import lochness
import argparse as ap
import lochness.config as config
from lochness.email import send_out_daily_updates


def parse_args(argv):
    parser = ap.ArgumentParser(description='PHOENIX data syncer')
    parser.add_argument('-c', '--config', required=True,
                        help='Configuration file')
    parser.add_argument('-l', '--log-file',
                        help='Log file')

    args = parser.parse_args(argv)
    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    Lochness = config.load(args.config, args.archive_base)
    Lochness['log_file'] = str(args.log_file)
    send_out_daily_updates(Lochness)
