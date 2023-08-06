# -*- coding: utf-8 -*-
"""
create on 2018-04-01 上午10:34

author @heyao
"""

from __future__ import unicode_literals, print_function

from datetime import datetime
from dateutil.relativedelta import relativedelta

from april3rd.loader import recall
from april3rd.utils import load_object


def accompany_last(from_date, to_date, to_dict=False):
    delta = relativedelta(to_date, from_date)
    if to_dict:
        return {
            'years': delta.years,
            'months': delta.months,
            'days': delta.days,
            'hours': delta.hours,
            'minutes': delta.minutes,
            'seconds': delta.seconds
        }
    return delta


def accompany_last_formatted(from_date, to_date, datefmt="{years}年{months}月{days}天{hours}小时{minutes}分{seconds}秒"):
    dt_info = accompany_last(from_date, to_date, to_dict=True)
    return datefmt.format(**dt_info)


def now():
    return datetime.now()


def get_experience():
    obj = recall()
    experience = obj['experience']
    return experience


def get_relationship():
    obj = recall()
    relation = obj['relationship'][-1]
    return relation


def get_accompany_start_date():
    relation = get_relationship()
    relation_date = relation['date']
    return relation_date


def get_accompany_obj():
    relation = get_relationship()
    relation_name = relation['name']
    relation_obj = load_object('april3rd.relationship.%s' % relation_name)
    relation_instance = relation_obj()
    return relation_instance


def show_anniversary():
    relation_date = get_accompany_start_date()
    accompany_date = accompany_last(relation_date, now(), to_dict=True)
    if accompany_date['years'] > 0 and accompany_date['months'] == 0 and accompany_date['days'] == 0:
        relation_instance = get_accompany_obj()
        print("{0:=^36}".format("%s和喝药药已经%s%s周年了！" %
                                (relation_instance.name, relation_instance.action, accompany_date['years'])))
        return True
    return False


def show_title():
    relation_instance = get_accompany_obj()
    b = show_anniversary()
    if not b:
        print("{0:=^40}".format("%s和喝药药已经%s" % (relation_instance.name, relation_instance.action)), flush=False)


def show_it_again(flush=True):
    relation_date = get_accompany_start_date()
    end = '\r' if flush else '\n'
    print("{0: ^44}".format(accompany_last_formatted(relation_date, now())), end=end, flush=flush)
