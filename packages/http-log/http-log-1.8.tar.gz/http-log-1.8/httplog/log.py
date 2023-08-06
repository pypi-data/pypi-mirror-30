# -*- coding: utf-8 -*-
# Copyright 2018 IFOOTH
# Author: Joe Lei <thezero12@hotmail.com>
"""自定义LOG"""
import logging


class SmartRespHandler(logging.FileHandler):
    def emit(self, record):
        msg = record.getMessage()
        if len(msg) > 1000:
            msg = '%s ... %s' % (msg[:500], msg[-500:])
        record.msg = msg
        super(SmartRespHandler, self).emit(record)
