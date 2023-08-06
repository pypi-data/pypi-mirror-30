# -*- coding: utf-8 -*-
# Copyright 2018 IFOOTH
# Author: Joe Lei <thezero12@hotmail.com>
"""httplib2支持
"""
from __future__ import absolute_import

import logging
import time

import httplib2

logger = logging.getLogger(__name__)


class Http(httplib2.Http):
    def request(self, *args, **kwargs):
        """添加LOG
        """
        st = time.time()

        body = kwargs.get('body')
        url = args[0]

        if len(args) == 1:
            method = 'GET'
        else:
            method = args[1]

        curl_req = "REQ: curl -X {method} '{url}'".format(method=method, url=url)
        if body:
            curl_req += " -d '{body}'".format(body=body)

        response, content = super(Http, self).request(*args, **kwargs)
        curl_resp = 'RESP: [%s] %.2fms %s' % (response.status, (time.time() - st) * 1000, content)

        logger.info('httplib2 - \n\t%s\n\t%s', curl_req, curl_resp)

        return (response, content)
