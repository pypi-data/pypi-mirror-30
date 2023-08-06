# -*- coding: utf-8 -*-
from __future__ import absolute_import

from pkg_resources import get_distribution

from .core import GabiaSMS
from .exceptions import SMSModuleException
from .shortcuts import (
    send,
    get_send_result,
    cancel_reservation
)

__version__ = get_distribution('gabia-sms-Django').version

__all__ = (
    'GabiaSMS',
    'SMSModuleException',
    'send',
    'get_send_result',
    'cancel_reservation'
)
