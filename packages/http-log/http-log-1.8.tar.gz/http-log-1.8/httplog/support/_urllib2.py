# -*- coding: utf-8 -*-
# Copyright 2018 IFOOTH
# Author: Joe Lei <thezero12@hotmail.com>
"""urllib2 urlopen支持"""
from __future__ import absolute_import
from functools import wraps
import logging

LOG_REQ = logging.getLogger('HTTP_REQ')
LOG_RESP = logging.getLogger('HTTP_RESP')


def http_log_wraper(open_func):
    """urlopen装饰器
    """
    @wraps(open_func)
    def _wrapped_view(*args, **kwargs):
        url = args[0]
        data = kwargs.get('data')
        if data:
            LOG_REQ.info("curl -X POST '%s' -d '%s'" % (url, data))
        else:
            LOG_REQ.info("curl -X GET '%s'" % url)

        resp = open_func(*args, **kwargs)
        content = resp.read()
        LOG_RESP.info('RESP(%s) %s' % (resp.code, content.decode("unicode-escape")))
        resp.read = lambda: content
        return resp
    return _wrapped_view
