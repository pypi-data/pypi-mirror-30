# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import requests
import inspect
import copy

from meituan.api.base import BaseMeituanPayAPI
from meituan import api
from meituan.utils import calculate_sign
from meituan.exceptions import *

class MeituanPay(object):
    """
    美团支付接口
    :param appId: 接入方标识，由美团开放平台分配
    :param appsecret: 
    """
    API_BASE_URL = 'https://openpay.meituan.com/'

    _http = requests.Session()

    micropay = api.MeituanMicroPay()

    def __new__(cls, *args, **kwargs):
        self = super(MeituanPay, cls).__new__(cls)
        api_endpoints = inspect.getmembers(self, lambda obj: isinstance(obj, BaseMeituanPayAPI))
        for name, _api in api_endpoints:
            api_cls = type(_api)
            _api = api_cls(self)
            setattr(self, name, _api)
        return self

    def __init__(self, appid, appsecret, merchant_id):
        self.appid = appid
        self.appsecret = appsecret
        self.merchant_id = merchant_id

    def _request(self, method, url_or_endpoint, **kwargs):
        url = '{0}{1}'.format(self.API_BASE_URL, url_or_endpoint)

        params = kwargs['params']
        if url_or_endpoint == 'api/pay/micropay':
            _params = copy.copy(params)
            if params.get('wxSubAppId'):
                del _params['wxSubAppId']
            random_string, sign = calculate_sign(self.appsecret, _params)
        else:
            random_string, sign = calculate_sign(self.appsecret, params)
        params['random'], params['sign'] = random_string, sign
        print(params)
        res = self._http.request(
            method=method,
            url=url,
            json=params
        )
        res.raise_for_status()
        return self._handle_result(res)

    def _handle_result(self, res):
        try:
            res = res.json()
        except:
            raise InvalidResponse('Meituan payment result json parsing error')
        if res['status'] == 'FAIL':
            raise MeituanPayException(
                errcode=res['errCode'],
                errmsg=res['errMsg'],
                subcode=res['subCode'],
                submsg=res['subMsg']
            )
        return res 

    def get(self, url, **kwargs):
        return self._request(
            method='get',
            url_or_endpoint=url,
            **kwargs
        )

    def post(self, url, **kwargs):
        return self._request(
            method='post',
            url_or_endpoint=url,
            **kwargs
        )
