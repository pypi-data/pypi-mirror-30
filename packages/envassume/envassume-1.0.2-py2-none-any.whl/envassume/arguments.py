# -*- coding: utf-8 -*-
"""
envassume arguments
"""

from __future__ import print_function
import os
from attr import attrs, attrib
from .exceptions import (
    EnvAssumeHelpException,
    EnvAssumeArgumentException,
    EnvAssumeMissingArnException,
    EnvAssumeMissingCommandException
)


@attrs
class Env(object):
    name = attrib()
    var = attrib()


ENV_LIST = (
    Env('arn', 'AWS_ASSUME_ROLE'),
    Env('external_id', 'AWS_ASSUME_ID'),
)


@attrs
class Option(object):
    name = attrib()
    arg_short = attrib()
    arg = attrib()


OPTION_LIST = (
    Option('external_id', '-i', '--id'),
)


def _pop_argument(arg_list):
    try:
        return arg_list.pop(0)

    except IndexError:
        return None


def _match_option(arg, arg_list):
    for option in OPTION_LIST:
        if arg == '-h' or arg == '--help':
            raise EnvAssumeHelpException

        elif arg == option.arg_short:
            return option.name, _pop_argument(arg_list)

        elif arg == option.arg:
            return option.name, _pop_argument(arg_list)

        elif arg.startswith(option.arg):
            arg_split = arg.split('=', 1)
            if arg_split[0] == option.arg and len(arg_split) == 2:
                return option.name, arg_split[1]

            raise EnvAssumeArgumentException('Invalid argument: {}'.format(arg))

        elif arg == '--':
            raise EnvAssumeMissingArnException('ARN not supplied')

    raise EnvAssumeArgumentException('Unknown argument: {}'.format(arg))


def parse_arguments(arg_list):
    # skip script name
    _pop_argument(arg_list)

    result = {}

    for env in ENV_LIST:
        env_val = os.environ.get(env.var)
        if env_val:
            result[env.name] = env_val

    if not result.get('arn'):
        while True:
            arg = _pop_argument(arg_list)

            if arg and arg.startswith('-'):
                option_name, option_value = _match_option(arg, arg_list)
                result[option_name] = option_value

            elif not arg:
                raise EnvAssumeMissingArnException('ARN not supplied')

            else:
                result['arn'] = arg
                break

    # skip optional separator
    if arg_list and arg_list[0] == '--':
        _pop_argument(arg_list)

    if not arg_list:
        raise EnvAssumeMissingCommandException('Command not supplied')

    result['command'] = arg_list

    return result
