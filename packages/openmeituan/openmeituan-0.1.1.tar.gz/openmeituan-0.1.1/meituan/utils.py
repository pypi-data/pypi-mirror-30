# -*- coding: utf-8 -*-
import random
import string
import hashlib
import copy
import datetime
import six


def generate_out_trade_no(merchant_id):
    return '{0}{1}{2}'.format(merchant_id, datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(1000, 10000))


def calculate_sign(appsecret, params):
    params = copy.copy(params)
    random_string = [random.choice(string.digits + string.ascii_letters) for i in range(32)]
    random.shuffle(random_string)
    random_string = ''.join(random_string)
    params['random'] = random_string
    joint_string = '&'.join(['{0}={1}'.format(i, params[i]) for i in sorted(params.keys())] + ['key={0}'.format(appsecret)])
    if six.PY2:
        sign = hashlib.sha256(joint_string).hexdigest()
    else:
        sign = hashlib.sha256(joint_string.encode('utf-8')).hexdigest()
    return random_string, sign
    

def to_text(value, encoding='utf-8'):
    """Convert value to unicode, default encoding is utf-8
    :param value: Value to be converted
    :param encoding: Desired encoding
    """
    if not value:
        return ''
    if isinstance(value, six.text_type):
        return value
    if isinstance(value, six.binary_type):
        return value.decode(encoding)
    return six.text_type(value)


def to_binary(value, encoding='utf-8'):
    """Convert value to binary string, default encoding is utf-8
    :param value: Value to be converted
    :param encoding: Desired encoding
    """
    if not value:
        return b''
    if isinstance(value, six.binary_type):
        return value
    if isinstance(value, six.text_type):
        return value.encode(encoding)
    return to_text(value).encode(encoding)
