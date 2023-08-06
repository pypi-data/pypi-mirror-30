# -*- coding: utf-8 -*-
# Copyright 2018 IFOOTH
# Author: Joe Lei <thezero12@hotmail.com>
"""requests支持
"""
from __future__ import absolute_import
import logging

from requests import sessions

LOG_REQ = logging.getLogger('HTTP_REQ')
LOG_RESP = logging.getLogger('HTTP_RESP')


class Session(sessions.Session):
    def request(self, *args, **kwargs):
        """添加LOG
        """
        response = super(Session, self).request(*args, **kwargs)
        prep = response.request
        if prep.method in ['GET']:
            LOG_REQ.info("curl -X %s '%s'" % (prep.method, prep.url))
        else:
            LOG_REQ.info("curl -X %s '%s' -d '%s'" % (
                prep.method, prep.url, prep.body))

        LOG_RESP.info('Resp(%s): %s' % (response.status_code, response.text.decode("unicode-escape")))
        return response
