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
    'fall_in_at': datetime(2017, 10, 3),
    'relationship': [{
        'name': 'GayFriend',
        'date': datetime(2013, 5, 1)
    }, {
        'name': 'GirlFriend',
        'date': datetime(2017, 10, 3)
    }]
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
