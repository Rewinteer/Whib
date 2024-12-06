import json

import redis

from webapp.config.redis_config import REDIS_DB, REDIS_HOST, REDIS_PORT
from webapp.logging_config import logger

r_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def get_cache_key(tg_chat_id, operation, flag=None):
    key = f'{tg_chat_id}:{operation}'
    if flag:
        key = key + f':{flag}'
    return key


def get_key_from_fun(db_func, arg_dict):
    tg_chat_id = arg_dict['tg_chat_id']
    operation = db_func.__name__
    flag = None
    for k, v in arg_dict.items():
        if k.endswith('_flag'):
            flag = v
            break
    return get_cache_key(tg_chat_id, operation, flag)


def get_chat_id(db_func, arg_dict):
    tg_chat_id = arg_dict['tg_chat_id']
    return tg_chat_id


def add_to_cache(key, result):
    try:
        json_result = json.dumps(result)
    except Exception as e:
        raise e

    r_conn.set(key, json_result)
    logger.info(f'added to redis entry with key: {key}')


def get_from_cache(key):
    result = r_conn.get(key)
    if result:
        deserialized_result = json.loads(result)
        logger.info(f'got from redis cache entry with key: {key}')
        return deserialized_result


def delete_from_cache(tg_chat_id):
    # r_conn.delete(key)
    logger.info(f'deleted from redis cache entry with pattern: {tg_chat_id}')
    for k in r_conn.scan_iter(f'{tg_chat_id}*'):
        r_conn.delete(k)


def cache_decorator(db_func):
    def wrapper(*args, **kwargs):
        key = get_key_from_fun(db_func, kwargs)
        cached = get_from_cache(key)
        if cached:
            return cached

        result = db_func(*args, **kwargs)
        if result:
            add_to_cache(key, result)
        return result

    return wrapper


def delete_cache_decorator(db_func):
    def wrapper(*args, **kwargs):
        tg_chat_id = get_chat_id(db_func, kwargs)
        result = db_func(*args, **kwargs)
        delete_from_cache(tg_chat_id)
        return result

    return wrapper


if __name__ == '__main__':
    delete_from_cache('234:get_visited:District')
