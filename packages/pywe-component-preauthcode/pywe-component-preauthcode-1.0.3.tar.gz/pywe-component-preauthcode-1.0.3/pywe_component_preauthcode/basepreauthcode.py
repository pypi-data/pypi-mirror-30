# -*- coding: utf-8 -*-

import time

from pywe_base import BaseWechat
from pywe_storage import MemoryStorage


class BasePreAuthCode(BaseWechat):
    def __init__(self, appid=None, secret=None, pre_auth_code=None, storage=None):
        super(BasePreAuthCode, self).__init__()
        self.appid = appid
        self.secret = secret
        self.pre_auth_code = pre_auth_code
        self.storage = storage or MemoryStorage()

        if self.pre_auth_code:
            expires_in = 1800
            component_preauthcode_info = {
                'pre_auth_code': self.pre_auth_code,
                'expires_in': expires_in,
                'expires_at': int(time.time()) + expires_in,
            }
            self.storage.set(self.component_preauthcode_info_key, component_preauthcode_info, expires_in)

    @property
    def component_preauthcode_info_key(self):
        return '{0}:component:access:info'.format(self.appid)

    def update_params(self, appid=None, secret=None, pre_auth_code=None, storage=None):
        self.appid = appid or self.appid
        self.secret = secret or self.secret
        self.pre_auth_code = pre_auth_code or self.pre_auth_code
        self.storage = storage or self.storage
