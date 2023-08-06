# -*- coding: utf-8 -*-
# Copyright 2018 IFOOTH
# Author: Joe Lei <thezero12@hotmail.com>
"""monkey patch"""
import sys
import traceback


def patch_httplib2():
    try:
        import httplib2
        from httplog.support._httplib2 import Http
        httplib2.Http = Http
    except ImportError:
        pass
    except Exception:
        traceback.print_exc()


def patch_requests():
    try:
        import requests
        from httplog.support._requests import Session
        requests.sessions.Session = Session
        requests.Session = Session
    except ImportError:
        pass
    except Exception:
        traceback.print_exc()


def patch_urlopen():
    try:
        import urllib2
        from httplog.support._urllib2 import http_log_wraper
        urllib2.urlopen = http_log_wraper(urllib2.urlopen)
    except Exception:
        traceback.print_exc()


def monkey_patch(httplib2=True, requests=True, urlopen=True):
    if httplib2:
        patch_httplib2()
    if requests:
        patch_requests()
    if urlopen:
        patch_urlopen()


if __name__ == "__main__":
    sys.argv.pop(0)
    monkey_patch()
    with open(sys.argv[0]) as f:
        code = compile(f.read(), sys.argv[0], 'exec')
        exec(code)
