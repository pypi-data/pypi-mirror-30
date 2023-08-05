# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import requests

from meituan.api.base import BaseMeituanPayAPI
from meituan.exceptions import *
from meituan.utils import generate_out_trade_no

class MeituanMicroPay(BaseMeituanPayAPI):
    def create(self, total_fee, auth_code, subject, body, 
            out_trade_no=None, expire_minutes=3, wx_subappid=None):
        """
        刷卡支付接口
        :param total_fee: 必填，总金额，单位分
        :param auth_code: 用户付款码
        :param body: 商品详情
        :param subject: 可选，商品标题
        :param expire_minutes: 可选，订单关闭时间，单位为分钟
        :param wx_subappid: 可选，微信公众号appid
        :return: 返回的结果数据
        """
        if not out_trade_no:
            out_trade_no = generate_out_trade_no(self.merchant_id)

        # SB接口有问题
        if not subject:
            subject = '美团刷码支付'

        channel = None
        if len(auth_code) == 18:
            auth_code_prefix = auth_code[:2]
            if auth_code_prefix in ['10', '11', '12', '13', '14', '15']:
                channel = 'wx_barcode_pay'
        elif 16 <= len(auth_code) <= 24:
            auth_code_prefix = auth_code[:2]
            if auth_code_prefix in ['25', '26', '27', '28', '29', '30']:
                channel = 'ali_barcode_pay'
        if channel == None:
            raise InvalidAuthCode(auth_code)
        params = {
            'channel': channel,
            'outTradeNo': out_trade_no,
            'authCode': auth_code,
            'totalFee': total_fee,
            'subject': subject,
            'body': body,
            'expireMinutes': expire_minutes,
            'merchantId': self.merchant_id,
            'appId': self.appid,
        }
        if wx_subappid:
            params['wxSubAppId'] = wx_subappid
        self._post('api/pay/micropay', params=params)

    def query(self, out_trade_no):
        """
        查询订单
        :param out_trade_no: 接入方订单号
        :return: 返回的结果数据
        """
        params = {
            'outTradeNo': out_trade_no,
            'merchantId': self.merchant_id,
            'appId': self.appid
        }
        return self._post('api/pay/query', params=params)