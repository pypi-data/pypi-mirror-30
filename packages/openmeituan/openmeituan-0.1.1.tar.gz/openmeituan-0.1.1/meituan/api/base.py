# -*- coding: utf-8 -*-

class BaseMeituanPayAPI(object):
    """ Meituan Pay API base class """
    def __init__(self, client=None):
        self._client = client
    
    def _get(self, url, **kwargs):
        return self._client.get(url, **kwargs)

    def _post(self, url, **kwargs):
        return self._client.post(url, **kwargs)

    @property
    def appid(self):
        return self._client.appid
        
    @property
    def merchant_id(self):
        return self._client.merchant_id
