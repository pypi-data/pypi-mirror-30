# -*- coding: utf-8 -*-
"""
envassume exceptions
"""


class EnvAssumeException(Exception):
    pass


class EnvAssumeHelpException(EnvAssumeException):
    pass


class EnvAssumeArgumentException(EnvAssumeException):
    pass


class EnvAssumeMissingArnException(EnvAssumeException):
    pass


class EnvAssumeMissingCommandException(EnvAssumeException):
    pass
