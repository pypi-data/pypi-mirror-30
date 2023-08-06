# -*- coding: utf-8 -*-
# Copyright 2018 IFOOTH
# Author: Joe Lei <thezero12@hotmail.com>
"""requests支持
"""
from __future__ import absolute_import

import logging
import time

from requests import sessions

logger = logging.getLogger(__name__)


class Session(sessions.Session):
    def request(self, *args, **kwargs):
        """添加LOG
        """
        st = time.time()
        response = super(Session, self).request(*args, **kwargs)
        prep = response.request

        # 添加日志信息
        curl_req = "REQ: curl -X {method} '{url}'".format(method=prep.method, url=prep.url)

        if prep.body:
            curl_req += " -d '{body}'".format(body=prep.body)

        if prep.headers:
            for header in prep.headers.items():
                # ignore headers
                if header[0] in ['User-Agent', 'Accept-Encoding', 'Connection', 'Accept', 'Content-Length']:
                    continue
                if header[0] == 'Cookie' and header[1].startswith('x_host_key'):
                    continue
                # curl_req += " -H '{k}: {v}'".format(k=header[0], v=header[1])

        curl_resp = 'RESP: [%s] %.2fms %s' % (response.status_code, (time.time() - st) * 1000, response.text)

        logger.info('requests - \n\t%s\n\t%s', curl_req, curl_resp)

        return response
