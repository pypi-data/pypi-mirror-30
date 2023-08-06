# -*- coding: utf-8 -*-
"""
create on 2018-03-31 下午7:34

author @heyao
"""
import base64
try:
    import cPickle as pickle
except ImportError:
    import pickle

from april3rd.memories import memory_path
from april3rd.secret import decrypt


def load_secret_attr():
    obj = recall('keep.pkl')
    return {key: base64.b64decode(obj[key]).decode('utf-8') for key in obj}


def load_key():
    return load_secret_attr()['key']


def load_iv():
    return load_secret_attr()['iv']


def recall(piece='time_machine.pkl'):
    with open(str(memory_path / piece), 'rb') as f:
        memory = f.read()
    if piece != "keep.pkl":
        memory = decrypt(memory, load_key(), load_iv())
    memory = pickle.loads(memory)
    return memory
