# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import six

from meituan.utils import to_binary, to_text

class InvalidAuthCode(Exception):
    def __init__(self, auth_code):
        err_msg = "invalid authcode: {0}".format(auth_code)
        Exception.__init__(self, err_msg)


class InvalidResponse(Exception):
    def __init__(self, err_msg):
        Exception.__init__(self, err_msg)


class MeituanPayException(Exception):
    def __init__(self, errcode, errmsg, subcode=None, submsg=None):
        """
        :param errcode: 错误编码
        :param errmsg: 错误消息描述
        :param subcode: 子错误码
        :param submsg: 子错误码的描述
        """
        self.errcode = errcode
        self.errmsg = errmsg
        self.subcode = subcode
        self.submsg = submsg
        
    def __str__(self):
        if six.PY2:
            return to_binary('Error code: {errcode}, message: {errmsg}. Subrror code: {subcode}, Submessage: {submsg}'.format(
                errcode=self.errcode,
                errmsg=self.errmsg,
                subcode=self.subcode,
                submsg=self.submsg
            ))
        else:
            return to_text('Error code: {errcode}, message: {errmsg}. Subrror code: {subcode}, Submessage: {submsg}'.format(
                errcode=self.errcode,
                errmsg=self.errmsg,
                subcode=self.subcode,
                submsg=self.submsg
            ))

    def __repr__(self):
        _repr = '{klass}({errcode}, {errmsg}). suberror({subcode}, {submsg})'.format(
            klass=self.__class__.__name__,
            errcode=self.errcode,
            errmsg=self.errmsg,
            subcode=self.subcode,
            submsg=self.submsg
        )
        if six.PY2:
            return to_binary(_repr)
        else:
            return to_text(_repr)
