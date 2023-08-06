# -*- coding: utf-8 -*-
"""
create on 2018-03-28 下午11:56

author @heyao
"""


class Li(object):
    def __init__(self, name):
        self._name = name
        self._experience = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val


class Classmate(Li):
    def __init__(self, name):
        super(Classmate, self).__init__(name)


class GayFriend(Classmate):
    def __init__(self, name):
        super(GayFriend, self).__init__(name)


class GirlFriend(GayFriend):
    def __init__(self, name="乖"):
        super(GirlFriend, self).__init__(name)

    @property
    def name(self):
        return '小乖乖'

    @name.setter
    def name(self, val):
        raise RuntimeError("can't set name")

    @property
    def action(self):
        return '在一起'

    @action.setter
    def action(self, val):
        raise RuntimeError("can't set action")


class Wife(GirlFriend):
    def __init__(self, name="乖"):
        super(Wife, self).__init__(name)
