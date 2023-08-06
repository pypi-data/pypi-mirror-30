# -*- coding: utf-8 -*-
"""
create on 2018-04-01 下午9:04

author @heyao
"""
from __future__ import absolute_import

from ..loader import load_cache
from ..experience.utils import now


def show_birthday():
    today = now()
    birth = load_cache()['data']
    if today.month == birth[0] and today.day == birth[1]:
        print("{0: ^40}".format("\033[1;31m 乖乖生日快乐哟~永远18岁~ \033[0m"))
