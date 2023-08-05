# -*- coding: utf-8 -*-

from furl import furl

from pywe_token import BaseToken, final_access_token


class MemberCard(BaseToken):
    def __init__(self, appid=None, secret=None, token=None, storage=None):
        super(MemberCard, self).__init__(appid=appid, secret=secret, token=token, storage=storage)
        # 卡券-小程序打通, Refer: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1499332673_Unm7V
        self.GET_ACTIVATE_URL = self.API_DOMAIN + '/card/membercard/activate/geturl'

    def get_activate_url(self, card_id, outer_str=None, appid=None, secret=None, token=None, storage=None):
        return self.post(
            self.GET_ACTIVATE_URL,
            params={
                'access_token': final_access_token(self, appid=appid, secret=secret, token=token, storage=storage),
            },
            data={
                'card_id': card_id,
                'outer_str': outer_str,
            },
        )

    def get_miniapp_extraData(self, card_id, outer_str=None, appid=None, secret=None, token=None, storage=None):
        data = self.get_activate_url(card_id, outer_str=outer_str, appid=appid, secret=secret, token=token, storage=storage)
        url = data.get('url', '')
        return dict(furl(url).args)


membercard = MemberCard()
get_activate_url = membercard.get_activate_url
get_miniapp_extraData = membercard.get_miniapp_extraData
