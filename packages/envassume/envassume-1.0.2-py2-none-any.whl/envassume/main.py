# -*- coding: utf-8 -*-
"""
envassume
"""

from __future__ import print_function
import sys
import os
from socket import gethostname
import boto3
from botocore.exceptions import BotoCoreError
from .exceptions import EnvAssumeException, EnvAssumeHelpException
from .arguments import parse_arguments
from .usage import print_help, print_error


def assume_role(role_arn, external_id = None, session_name = None):
    if not external_id:
        external_id = os.environ.get('AWS_EXTERNAL_ID')

    if not session_name:
        session_name = 'envassume-' + gethostname()

    request = {
        'RoleArn': role_arn,
        'RoleSessionName': session_name
    }

    if external_id:
        request['ExternalId'] = external_id

    boto3_session = boto3.Session()
    sts_client = boto3_session.client('sts')
    try:
        response = sts_client.assume_role(**request)

    except BotoCoreError as e:
        raise EnvAssumeException(e.message)

    return response.get('Credentials') or {}


def update_env(credentials_lookup):
    credentials_list = (
        ('AccessKeyId', 'AWS_ACCESS_KEY_ID'),
        ('SecretAccessKey', 'AWS_SECRET_ACCESS_KEY'),
        ('SessionToken', 'AWS_SESSION_TOKEN'),
    )
    for credential_key, env_var_name in credentials_list:
        os.environ[env_var_name] = credentials_lookup[credential_key]


def exec_command(arg_list):
    try:
        os.execvpe(arg_list[0], arg_list, os.environ)

    except OSError as e:
        raise EnvAssumeException('Unable to run command {}: {}'.format(arg_list[0], e))

    raise EnvAssumeException('Unable to run command {}'.format(arg_list[0]))


def envassume():
    arg_lookup = parse_arguments(sys.argv)

    credentials_lookup = assume_role(arg_lookup.get('arn'), arg_lookup.get('external_id'))

    update_env(credentials_lookup)

    exec_command(arg_lookup['command'])


def run():
    try:
        envassume()

    except EnvAssumeHelpException:
        print_help()

    except EnvAssumeException as e:
        print_error(e)
        sys.exit(1)

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run()
