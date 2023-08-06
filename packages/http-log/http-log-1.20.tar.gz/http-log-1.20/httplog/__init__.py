# -*- coding: utf-8 -*
# Copyright 2015 Tencent
# Author: Joe Lei <joelei@tencent.com>
import logging.config
import os.path

from httplog import patcher

monkey_patch = patcher.monkey_patch

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'httplog': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.expanduser('~') + '/httplog.log',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'httplog': {
            'handlers': ['httplog'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

logging.config.dictConfig(LOGGING)


__VERSION__ = '1.20'
