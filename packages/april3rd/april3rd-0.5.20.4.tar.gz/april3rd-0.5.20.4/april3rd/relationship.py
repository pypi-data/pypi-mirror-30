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
        raise RuntimeError("任何人都不能改我乖的名字！")

    @property
    def action(self):
        return '在一起'

    @action.setter
    def action(self, val):
        raise RuntimeError("任何人都不能阻止我和乖%s！" % self.action)

    @property
    def key(self):
        return 'gf'

    @key.setter
    def key(self, val):
        raise RuntimeError("谁叫你改的？？")


class Wife(GirlFriend):
    def __init__(self, name="乖"):
        super(Wife, self).__init__(name)

    @property
    def name(self):
        return '老婆'

    @name.setter
    def name(self, val):
        raise RuntimeError("任何人都不能改我%s的名字！" % self.name)

    @property
    def action(self):
        return '结婚'

    @action.setter
    def action(self, val):
        raise RuntimeError("任何人都不能阻止我和乖%s！" % self.action)

    @property
    def key(self):
        return 'wife'

    @key.setter
    def key(self, val):
        raise RuntimeError("谁叫你改的？？")
