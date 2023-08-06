# -*- coding: utf-8 -*-


def get_pre_auth_url(component_appid, pre_auth_code=None, redirect_uri=None, auth_type=3):
    return 'https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid={component_appid}&pre_auth_code={pre_auth_code}&redirect_uri={redirect_uri}&auth_type={auth_type}'.format(
        component_appid=component_appid,
        pre_auth_code=pre_auth_code,
        redirect_uri=redirect_uri,
        auth_type=auth_type
    )
