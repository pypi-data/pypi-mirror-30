===============
pywe-membercard
===============

Wechat MemberCard Module for Python.

Installation
============

::

    pip install pywe-membercard


Usage
=====

::

    from pywe_membercard import MemberCard, get_activate_url, get_miniapp_extraData


Method
======

::

    class MemberCard(BaseToken):
        def __init__(self, appid=None, secret=None, token=None, storage=None):
            super(MemberCard, self).__init__(appid=appid, secret=secret, token=token, storage=storage)

    def get_activate_url(self, card_id, outer_str=None, appid=None, secret=None, token=None, storage=None):

    def get_miniapp_extraData(self, card_id, outer_str=None, appid=None, secret=None, token=None, storage=None):



