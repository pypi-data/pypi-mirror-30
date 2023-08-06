# -*- coding: utf-8 -*-

import time

from pywe_component_token import component_access_token
from pywe_exception import WeChatException

from .basepreauthcode import BasePreAuthCode


class PreAuthCode(BasePreAuthCode):
    def __init__(self, appid=None, secret=None, storage=None):
        super(PreAuthCode, self).__init__(appid=appid, secret=secret, storage=storage)
        # 授权流程技术说明, Refer: https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1453779503&token=&lang=zh_CN
        # 3、获取预授权码pre_auth_code
        # 该API用于获取预授权码。预授权码用于公众号或小程序授权时的第三方平台方安全验证。
        self.WECHAT_COMPONENT_PREAUTHCODE = self.API_DOMAIN + '/cgi-bin/component/api_create_preauthcode?component_access_token={component_access_token}'

    def __about_to_expires(self, expires_at):
        return expires_at and expires_at - int(time.time()) < 60

    def __fetch_component_preauthcode(self, appid=None, secret=None, storage=None):
        # Update Params
        self.update_params(appid=appid, secret=secret, storage=storage)
        # Component PreAuthCode Request
        token = component_access_token(appid=self.appid, secret=self.secret, storage=self.storage)
        component_preauthcode_info = self.post(self.WECHAT_COMPONENT_PREAUTHCODE.format(component_access_token=token), data={
            'component_appid': self.appid,
        })
        # Request Error
        if 'expires_in' not in component_preauthcode_info:
            raise WeChatException(component_preauthcode_info)
        # Set Component PreAuthCode into Storage
        expires_in = component_preauthcode_info.get('expires_in')
        component_preauthcode_info['expires_at'] = int(time.time()) + expires_in
        self.storage.set(self.component_preauthcode_info_key, component_preauthcode_info, expires_in)
        # Return Component PreAuthCode
        return component_preauthcode_info.get('pre_auth_code')

    def component_preauthcode(self, appid=None, secret=None, storage=None):
        # Update Params
        self.update_params(appid=appid, secret=secret, storage=storage)
        # Fetch component_preauthcode_info
        component_preauthcode_info = self.storage.get(self.component_preauthcode_info_key)
        if component_preauthcode_info:
            pre_auth_code = component_preauthcode_info.get('pre_auth_code')
            if pre_auth_code and not self.__about_to_expires(component_preauthcode_info.get('expires_at')):
                return pre_auth_code
        return self.__fetch_component_preauthcode(appid, secret, storage)

    def refresh_component_preauthcode(self, appid=None, secret=None, storage=None):
        return self.__fetch_component_preauthcode(appid, secret, storage)

    def final_component_preauthcode(self, cls=None, appid=None, secret=None, pre_auth_code=None, storage=None):
        return pre_auth_code or self.component_preauthcode(appid or cls.appid, secret or cls.secret, storage=storage or cls.storage)


preauthcode = PreAuthCode()
component_preauthcode = preauthcode.component_preauthcode
refresh_component_preauthcode = preauthcode.refresh_component_preauthcode
final_component_preauthcode = preauthcode.final_component_preauthcode
