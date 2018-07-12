#!/usr/bin/env python
import argparse
import sys


def get_parser():
    parser = argparse.ArgumentParser(description='Fixture to support checklisting.tasks.subprocess testing')
    parser.add_argument('--stdout', dest='stdout', help='Print given value to STDOUT')
    parser.add_argument('--stderr', dest='stderr', help='Print given value to STDERR')
    parser.add_argument('--exit', dest='exit', type=int, help='Exit with given status')

    return parser.parse_args()


def main():
    args = get_parser()
    if args.stdout:
        sys.stdout.write(args.stdout)
    if args.stderr:
        sys.stderr.write(args.stderr)
    if args.exit:
        sys.exit(args.exit)


if '__main__' == __name__:
    main()
