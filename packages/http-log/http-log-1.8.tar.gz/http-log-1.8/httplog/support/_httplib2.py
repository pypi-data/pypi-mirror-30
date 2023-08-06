# -*- coding: utf-8 -*-
# Copyright 2018 IFOOTH
# Author: Joe Lei <thezero12@hotmail.com>
"""httplib2支持
"""
from __future__ import absolute_import
import logging

import httplib2

LOG_REQ = logging.getLogger('HTTP_REQ')
LOG_RESP = logging.getLogger('HTTP_RESP')


class Http(httplib2.Http):
    def request(self, *args, **kwargs):
        """添加LOG
        """
        uri = args[0]
        method = args[1]
        body = kwargs.get('body')
        if body:
            LOG_REQ.info("curl -X %s '%s' -d '%s' " % (method, uri, body))
        else:
            LOG_REQ.info("curl -X %s '%s'" % (method, uri))

        response, content = super(Http, self).request(*args, **kwargs)
        LOG_RESP.info('Resp(%s): %s' % (response.status, content.decode("unicode-escape")))
        return (response, content)
