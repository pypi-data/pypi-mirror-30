# -*- coding: utf-8 -*-
"""
create on 2018-03-29 上午12:36

author @heyao
"""
try:
    import cPickle as pickle
except ImportError:
    import pickle
import base64
from datetime import datetime
from april3rd.loader import load_key, load_iv
from april3rd.secret import encrypt

data = {
    'info': {
        'birth_date': (4, 3),
        'birthday': (3, 4)
    },
    'fall_in_at': datetime(2017, 10, 3),
    'relationship': [{
        'name': 'GayFriend',
        'date': datetime(2013, 5, 1)
    }, {
        'name': 'GirlFriend',
        'date': datetime(2017, 10, 3)
    }],
    'experience': [
        {'date': datetime(2013, 2, 19), 'action': {'gf': '在尔静桥第一次相遇。', 'wife': '在尔静桥第一次相遇。'}},
        {'date': datetime(2013, 5, 1), 'action': {'gf': '第一次一起刷夜。', 'wife': '第一次一起刷夜。'}},
        {'date': datetime(2014, 5, 1), 'action': {'gf': '是建模哦~', 'wife': '是建模哦~'}},
        {'date': datetime(2014, 9, 8), 'action': {'gf': '第一次通宵唱歌。', 'wife': '第一次通宵唱歌。'}},
        {'date': datetime(2016, 6, 30), 'action': {'gf': '喝药去了杭州，而她在学习继续读书。', 'wife': '喝药去杭州浪了哈哈哈！'}},
        {'date': datetime(2017, 10, 3), 'action': {'gf': '在一起了❤️', 'wife': '在一起了❤️'}},
        {'date': datetime(2018, 3, 27), 'action': {'gf': '乖乖第一次面试，紧张哦~', 'wife': '第一次面试，稳中带皮，皮中带稳。'}}
    ]
}
with open('/Users/heyao/april3rd/april3rd/memories/time_machine.pkl', 'wb') as f:
    data = pickle.dumps(data, protocol=2)
    f.write(encrypt(data, load_key(), load_iv()))

keys = {
    'iv': 'lovexiaoguaiguai',
    'key': 'onlyloveguaiguai'
}
with open('/Users/heyao/april3rd/april3rd/memories/keep.pkl', 'wb') as f:
    keys = {key: base64.b64encode(keys[key].encode('utf-8')) for key in keys}
    pickle.dump(keys, f, protocol=2)
