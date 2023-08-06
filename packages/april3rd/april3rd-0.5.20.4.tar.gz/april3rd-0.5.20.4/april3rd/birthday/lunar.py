# -*- coding: utf-8 -*-
"""
create on 2018-04-01 下午7:28

author @heyao
"""
import time
import json
from datetime import datetime
try:
    import cPickle as pickle
except ImportError:
    import pickle

import requests
from april3rd.experience.utils import now, accompany_last
from april3rd.loader import load_key, load_iv, recall
from april3rd.memories import memory_path
from april3rd.secret import encrypt


def get_lunar_date(date):
    url = 'https://www.sojson.com/open/api/lunar/json.shtml?date={date}'.format(date=date)
    response = requests.get(url)
    content = response.content
    response.close()
    json_data = json.loads(content)
    real = (json_data['data']['month'], json_data['data']['day'])
    lunar_real = (json_data['data']['lunarMonth'], json_data['data']['lunarDay'])
    return real, lunar_real


def generate_maybe_lunar_date(lunar_date=None, real_lunar_date=None):
    if lunar_date is None:
        return 4, 1, 0, 0
    year = now().year
    delta = accompany_last(datetime(year, real_lunar_date[0], real_lunar_date[1]), datetime(year, lunar_date[0], lunar_date[1]))
    month_delta = delta.months
    days_delta = delta.days
    return (lunar_date[0] - month_delta, lunar_date[1] - days_delta), month_delta, days_delta


def get_lunar_birthday():
    real_lunar_date = recall()['info']['birthday']
    return real_lunar_date


def search_birthday():
    stop = False
    real_lunar_date = get_lunar_birthday()
    year = now().year
    real = (4, 1)
    max_retry_times = 10
    retries = 0
    while not stop:
        real, lunar_date = get_lunar_date('%s-%s-%s' % (year, real[0], real[1]))
        if lunar_date == real_lunar_date:
            return real
        lunar_date, month_delta, days_delta = generate_maybe_lunar_date(lunar_date, real_lunar_date)
        real = (real[0] - month_delta, real[1] - days_delta)
        retries += 1
        if retries >= max_retry_times:
            break
        time.sleep(3)


def cache_birthday_for_year(birthday, year=now().year):
    with open(str(memory_path / 'cache_birthday.pkl'), 'wb') as f:
        birthday = pickle.dumps({'data': birthday, 'year': year})
        birthday = encrypt(birthday, load_key(), load_iv())
        f.write(birthday)
