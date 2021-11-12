import redis
from flask import current_app
from os import getenv
import dateutil
import datetime
import copy
import ujson

pool: redis.ConnectionPool = None

def init():
    global pool
    pool = redis.ConnectionPool(host=getenv('REDIS_HOST'), port=getenv('REDIS_PORT'), password=getenv('REDIS_PASSWORD'), db=0)
    return pool

def init_mq():
    global mq_pool
    mq_pool = redis.ConnectionPool(host=getenv('REDIS_HOST'), port=getenv('REDIS_PORT'), password=getenv('REDIS_PASSWORD'), db=1)
    return mq_pool

def get_pool():
    global pool
    return pool

def get_conn():
    return redis.Redis(connection_pool=pool)

def get_mq_conn():
    return redis.Redis(connection_pool=mq_pool)

def serialize_dict(data):
    to_serialize = {
        'dates': [],
        'data': {}
    }

    for key, value in data.items():
        if type(value) is datetime.datetime:
            to_serialize['dates'].append(key)
            to_serialize['data'][key] = value.isoformat()
        else:
            to_serialize['data'][key] = value

    return ujson.dumps(to_serialize)

def deserialize_dict(data):
    data = ujson.loads(data)
    to_return = {}
    for key, value in data['data'].items():
        if key in data['dates']:
            to_return[key] = dateutil.parser.parse(value)
        else:
            to_return[key] = value
    return to_return

def serialize_dict_list(data):
    data = copy.deepcopy(data)
    return ujson.dumps(list(map(lambda elem: serialize_dict(elem), data)))

def deserialize_dict_list(data):
    data = ujson.loads(data)
    to_return = list(map(lambda elem: deserialize_dict(elem), data))
    return to_return

def delete_keys(pattern):
    redis = get_conn()
    keys = redis.keys(pattern)
    if (len(keys)):
        redis.delete(*keys)