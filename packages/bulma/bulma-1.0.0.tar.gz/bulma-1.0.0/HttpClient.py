#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/24 上午8:15
# @Author  : Dirk Zhao
import requests
from Log import logger


METHODS = ['GET', 'POST', 'HEAD', 'TRACE', 'PUT', 'DELETE', 'OPTIONS', 'CONNECT']


class UnSupportMethodException(Exception):
    pass


class HttpClient():

    def __init__(self, url, method='GET', headers=None, cookies=None):
        '''__init__方法必须传入url，默认请求方式为GET'''
        self.url = url
        self.session = requests.session()
        self.method = method.upper()
        if self.method not in METHODS:
            raise UnSupportMethodException('不支持的method:{0},请检查传入参数'.format(self.method))
        self.set_headers(headers)
        self.set_cookies(headers)

    def set_headers(self, headers):
        if headers:
            self.session.headers.update(headers)

    def set_cookies(self, cookies):
        if cookies:
            self.session.cookies.update(cookies)

    def send(self, params=None, data=None, **kwargs):
        '''GET方法传入params，POST方法传入data'''
        response = self.session.request(method=self.method, url=self.url, params=params, data=data, **kwargs)
        response.encoding = 'utf-8'
        logger.debug('{0}{1}'.format(self.method, self.url))
        logger.debug('请求成功：{0}\n{1}'.format(response, response.text))
        return response
