# -*- coding: utf-8 -*-

from pywe_token import BaseToken, final_access_token


class QRCode(BaseToken):
    def __init__(self, appid=None, secret=None, token=None, storage=None):
        super(QRCode, self).__init__(appid=appid, secret=secret, token=token, storage=storage)
        # 生成带参数的二维码, Refer: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1443433542
        # 创建二维码ticket
        self.WECHAT_QRCODE_CREATE = self.API_DOMAIN + '/cgi-bin/qrcode/create'
        # 通过ticket换取二维码
        self.WECHAT_SHOW_QRCODE = self.MP_DOMAIN + '/cgi-bin/showqrcode?ticket={ticket}'

    def create(self, action_name='QR_SCENE', scene_id=0, scene_str='', expire_seconds=2592000, appid=None, secret=None, token=None, storage=None):
        """
        ``action_name`` 二维码类型，QR_SCENE为临时的整型参数值，QR_STR_SCENE为临时的字符串参数值，QR_LIMIT_SCENE为永久的整型参数值，QR_LIMIT_STR_SCENE为永久的字符串参数值
        ``scene_id``场景值ID，临时二维码时为32位非0整型，永久二维码时最大值为100000（目前参数只支持1--100000）
        ``scene_str``场景值ID（字符串形式的ID），字符串类型，长度限制为1到64
        ``expire_seconds`` 该二维码有效时间，以秒为单位。 最大不超过2592000（即30天），此字段如果不填，则默认有效期为30秒。
        """
        if action_name == 'QR_SCENE':
            data = {
                'expire_seconds': expire_seconds,
                'action_name': action_name,
                'action_info': {
                    'scene': {
                        'scene_id': scene_id
                    }
                }
            }
        elif action_name == 'QR_STR_SCENE':
            data = {
                'expire_seconds': expire_seconds,
                'action_name': action_name,
                'action_info': {
                    'scene': {
                        'scene_str': scene_str
                    }
                }
            }
        elif action_name == 'QR_LIMIT_SCENE':
            data = {
                'action_name': action_name,
                'action_info': {
                    'scene': {
                        'scene_id': scene_id
                    }
                }
            }
        elif action_name == 'QR_LIMIT_STR_SCENE':
            data = {
                'action_name': action_name,
                'action_info': {
                    'scene': {
                        'scene_str': scene_str
                    }
                }
            }

        return self.post(
            self.WECHAT_QRCODE_CREATE,
            params={
                'access_token': final_access_token(self, appid=appid, secret=secret, token=token, storage=storage),
            },
            data=data
        )

    def create_scene(self, scene_id=0, expire_seconds=2592000, appid=None, secret=None, token=None, storage=None):
        return self.create(action_name='QR_SCENE', scene_id=scene_id, expire_seconds=expire_seconds, appid=appid, secret=secret, token=token, storage=storage)

    def create_str_scene(self, scene_str='', expire_seconds=2592000, appid=None, secret=None, token=None, storage=None):
        return self.create(action_name='QR_STR_SCENE', scene_str=scene_str, expire_seconds=expire_seconds, appid=appid, secret=secret, token=token, storage=storage)

    def create_limit_scene(self, scene_id=0, appid=None, secret=None, token=None, storage=None):
        return self.create(action_name='QR_LIMIT_SCENE', scene_id=scene_id, appid=appid, secret=secret, token=token, storage=storage)

    def create_limit_str_scene(self, scene_str='', appid=None, secret=None, token=None, storage=None):
        return self.create(action_name='QR_LIMIT_STR_SCENE', scene_str=scene_str, appid=appid, secret=secret, token=token, storage=storage)

    def download(self, ticket):
        return self.get(self.WECHAT_SHOW_QRCODE, ticket=ticket, res_to_json=False)

    def showurl(self, ticket):
        return self.geturl(self.WECHAT_SHOW_QRCODE, ticket=ticket)


qrcode = QRCode()
qrcode_create = qrcode.create
qrcode_scene = qrcode.create_scene
qrcode_str_scene = qrcode.create_str_scene
qrcode_limit_scene = qrcode.create_limit_scene
qrcode_limit_str_scene = qrcode.create_limit_str_scene
qrcode_download = qrcode.download
qrcode_show = qrcode_url = qrcode.showurl
