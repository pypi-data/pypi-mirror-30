# -*- coding: utf-8 -*-
"""
envassume usage
"""

from __future__ import print_function
import sys


def print_help(short = False):
    print('usage: envassume [-h] [-i EXTERNAL_ID] [ARN] command [argument [argument ...]]', file = sys.stderr)
    if not short:
        print('''
optional arguments:
    -h, --help              show this help message and exit
    -i, --id EXTERNAL_ID    external id
    ARN                     AWS role ARN to assume (required if not set by environment variable)

environment variables:
    environment must contain valid AWS API credentials

    AWS_ASSUME_ROLE=ARN
        no options can be present before the command if this is defined

    AWS_ASSUME_ID=EXTERNAL_ID
''', file = sys.stderr)


def print_error(message):
    print_help(short = True)
    print('error: {}'.format(message), file = sys.stderr)
