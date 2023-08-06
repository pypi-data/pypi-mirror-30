# -*- coding: utf-8 -*-
# Copyright 2018 IFOOTH
# Author: Joe Lei <thezero12@hotmail.com>
"""urllib2 urlopen支持"""
from __future__ import absolute_import

import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def http_log_wraper(open_func):
    """urlopen装饰器
    """
    @wraps(open_func)
    def _wrapped_view(*args, **kwargs):
        st = time.time()
        url = args[0]
        data = kwargs.get('data')
        if data:
            curl_req = "REQ: curl -X POST '%s' -d '%s'" % (url, data)
        else:
            curl_req = "REQ: curl -X GET '%s'" % url

        resp = open_func(*args, **kwargs)
        content = resp.read()

        curl_resp = 'RESP: [%s] %.2fms %s' % (resp.code, (time.time() - st) * 1000, content)
        logger.info('urllib2 - \n\t%s\n\t%s', curl_req, curl_resp)

        resp.read = lambda: content
        return resp
    return _wrapped_view
