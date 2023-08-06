===========
pywe-qrcode
===========

Wechat QRCode Module for Python.

Sandbox
=======

* https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login

Installation
============

::

    pip install pywe-qrcode


Usage
=====

::

    from pywe_qrcode import QRCode, qrcode_create, qrcode_scene, qrcode_str_scene, qrcode_limit_scene, qrcode_limit_str_scene, qrcode_download, qrcode_show, qrcode_url


Method
======

::

    class QRCode(BaseToken):
        def __init__(self, appid=None, secret=None, token=None, storage=None):
            super(QRCode, self).__init__(appid=appid, secret=secret, token=token, storage=storage)

    def create(self, action_name='QR_SCENE', scene_id=0, scene_str='', expire_seconds=2592000, appid=None, secret=None, token=None, storage=None):

    def create_scene(self, scene_id=0, expire_seconds=2592000, appid=None, secret=None, token=None, storage=None):

    def create_str_scene(self, scene_str='', expire_seconds=2592000, appid=None, secret=None, token=None, storage=None):

    def create_limit_scene(self, scene_id=0, appid=None, secret=None, token=None, storage=None):

    def create_limit_str_scene(self, scene_str='', appid=None, secret=None, token=None, storage=None):

    def download(self, ticket):

    def showurl(self, ticket):

