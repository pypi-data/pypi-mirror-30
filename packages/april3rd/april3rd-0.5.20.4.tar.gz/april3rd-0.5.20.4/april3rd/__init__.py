# -*- coding: utf-8 -*-
"""
create on 2018-03-28 上午12:58

author @heyao
"""
from __future__ import absolute_import
from april3rd.experience.utils import show_it_again, show_title as _show_title
from april3rd.experience.show import accompany

from .birthday import cache_birthday_for_year, search_birthday, show_birthday as _show_birthday
from .loader import load_cache
from .experience.utils import now


cache = load_cache()
if not cache or cache['year'] != now().year:
    print("喝药正在做一些准备工作，可能会花10s左右的时间，请等待~")
    new_birthday = None
    try:
        new_birthday = search_birthday()
    except Exception as e:
        print("出了一点问题", e)
    if new_birthday:
        cache_birthday_for_year(new_birthday, now().year)

_show_birthday()
_show_title()
show_it_again(False)
