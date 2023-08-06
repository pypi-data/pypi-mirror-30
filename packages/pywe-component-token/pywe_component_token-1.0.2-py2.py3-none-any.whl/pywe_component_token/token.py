# -*- coding: utf-8 -*-

import time

from pywe_component_ticket import get_component_verify_ticket
from pywe_exception import WeChatException

from .basetoken import BaseComponentToken


class ComponentToken(BaseComponentToken):
    def __init__(self, appid=None, secret=None, storage=None):
        super(ComponentToken, self).__init__(appid=appid, secret=secret, storage=storage)
        # 授权流程技术说明, Refer: https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1453779503&token=&lang=zh_CN
        # 第三方平台component_access_token是第三方平台的下文中接口的调用凭据，也叫做令牌（component_access_token）。
        # 每个令牌是存在有效期（2小时）的，且令牌的调用不是无限制的，请第三方平台做好令牌的管理，在令牌快过期时（比如1小时50分）再进行刷新。
        self.WECHAT_COMPONENT_TOKEN = self.API_DOMAIN + '/cgi-bin/component/api_component_token'

    def __about_to_expires(self, expires_at):
        return expires_at and expires_at - int(time.time()) < 60

    def __fetch_component_access_token(self, appid=None, secret=None, component_verify_ticket=None, storage=None):
        # Update Params
        self.update_params(appid=appid, secret=secret, storage=storage)
        # Component Access Info Request
        component_access_info = self.post(self.WECHAT_COMPONENT_TOKEN, data={
            'component_appid': self.appid,
            'component_appsecret': self.secret,
            'component_verify_ticket': component_verify_ticket or get_component_verify_ticket(appid=self.appid, secret=self.secret, storage=self.storage),
        })
        # Request Error
        if 'expires_in' not in component_access_info:
            raise WeChatException(component_access_info)
        # Set Access Info into Storage
        expires_in = component_access_info.get('expires_in')
        component_access_info['expires_at'] = int(time.time()) + expires_in
        self.storage.set(self.component_access_info_key, component_access_info, expires_in)
        # Return Access Token
        return component_access_info.get('component_access_token')

    def component_access_token(self, appid=None, secret=None, component_verify_ticket=None, storage=None):
        # Update Params
        self.update_params(appid=appid, secret=secret, storage=storage)
        # Fetch component_access_info
        component_access_info = self.storage.get(self.component_access_info_key)
        if component_access_info:
            component_access_token = component_access_info.get('component_access_token')
            if component_access_token and not self.__about_to_expires(component_access_info.get('expires_at')):
                return component_access_token
        return self.__fetch_component_access_token(appid, secret, component_verify_ticket, storage)

    def refresh_component_access_token(self, appid=None, secret=None, component_verify_ticket=None, storage=None):
        return self.__fetch_component_access_token(appid, secret, component_verify_ticket, storage)

    def final_component_access_token(self, cls=None, appid=None, secret=None, token=None, component_verify_ticket=None, storage=None):
        return token or self.component_access_token(appid or cls.appid, secret or cls.secret, component_verify_ticket, storage=storage or cls.storage)


token = ComponentToken()
component_access_token = token.component_access_token
refresh_component_access_token = token.refresh_component_access_token
final_component_access_token = token.final_component_access_token
