# -*- coding: utf-8 -*
# Copyright 2015 Tencent
# Author: Joe Lei <joelei@tencent.com>
import logging.config
import os.path

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
        'smart_req': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.expanduser('~') + '/httplog.log',
            'formatter': 'simple'
        },
        'smart_resp': {
            'level': 'DEBUG',
            'class': 'httplog.log.SmartRespHandler',
            'filename': os.path.expanduser('~') + '/httplog.log',
            'formatter': 'simple'
        },
        'detail': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.expanduser('~') + '/httplog.log.detail',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'HTTP_REQ': {
            'handlers': ['detail', 'smart_req'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'HTTP_RESP': {
            'handlers': ['detail', 'smart_resp'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

logging.config.dictConfig(LOGGING)

__VERSION__ = '1.8'

from httplog import patcher
patcher.monkey_patch()
