# -*- coding: utf-8 -*-
"""
create on 2018-04-01 上午10:38

author @heyao
"""
import time
import signal

from april3rd.experience.utils import show_title, show_it_again, get_experience, get_accompany_obj


def show_experience(experience):
    obj = get_accompany_obj()
    key = obj.key
    date = experience['date']
    action = experience['action']
    print(date.strftime("%Y{0}%m{1}%d{2}").format('年', '月', '日'), action[key])


class Accompany(object):
    def __init__(self):
        self.not_stop = 1
        self.experience = get_experience()

    def handler(self, signum, frame):
        self.not_stop = 0

    def show_experience(self):
        if not len(self.experience):
            print("本次已经看过了，下次再看吧~")
            return
        self.not_stop = 1
        signal.signal(signal.SIGINT, self.handler)
        while len(self.experience) and self.not_stop:
            experience = self.experience.pop(0)
            show_experience(experience)
            time.sleep(1)

    def run(self):
        show_title()
        self.not_stop = 1
        signal.signal(signal.SIGINT, self.handler)
        while self.not_stop:
            show_it_again()
            time.sleep(1)


accompany = Accompany()
