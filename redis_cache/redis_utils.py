import numpy as np
import bson.json_util as json_util
import redis


class Cache:
    def __init__(self):
        self.conn = redis.Redis(host='192.168.1.2', port=6379)
        self.conn.config_set('maxmemory', '100mb')
        self.conn.config_set('maxmemory-policy', 'allkeys-lru')

    def get_musers(self, uids):
        parsed_uids = list(map(lambda x: f'user_{x}', uids))
        cache_res = self.conn.mget(parsed_uids)
        res = list(map(lambda x: json_util.loads(x.decode('utf-8')) if x is not None else None, cache_res))
        return res, np.argwhere(np.array(res) == None).reshape(-1), np.argwhere(np.array(res) != None).reshape(-1)

    def set_musers(self, uids, jsons):
        parsed_uids = list(map(lambda x: f'user_{x}', uids))
        parsed_jsons = list(map(lambda x: json_util.dumps(x), jsons))
        self.conn.mset(dict(zip(parsed_uids, parsed_jsons)))

    def delete_user(self, uid):
        self.conn.delete(f'user_{uid}')

    def get_marticles(self, aids):
        parsed_aids = list(map(lambda x: f'article_{x}', aids))
        cache_res = self.conn.mget(parsed_aids)
        res = list(map(lambda x: json_util.loads(x.decode('utf-8')) if x is not None else None, cache_res))
        return res, np.argwhere(np.array(res) == None).reshape(-1), np.argwhere(np.array(res) != None).reshape(-1)

    def set_marticles(self, aids, jsons):
        parsed_aids = list(map(lambda x: f'article_{x}', aids))
        parsed_jsons = list(map(lambda x: json_util.dumps(x), jsons))
        self.conn.mset(dict(zip(parsed_aids, parsed_jsons)))

    def get_mreads(self, ids):
        parsed_ids = list(map(lambda x: f'read_{x}', ids))
        cache_res = self.conn.mget(parsed_ids)
        res = list(map(lambda x: json_util.loads(x.decode('utf-8')) if x is not None else None, cache_res))
        return res, np.argwhere(np.array(res) == None).reshape(-1), np.argwhere(np.array(res) != None).reshape(-1)

    def set_mreads(self, ids, jsons):
        parsed_ids = list(map(lambda x: f'read_{x}', ids))
        parsed_jsons = list(map(lambda x: json_util.dumps(x), jsons))
        self.conn.mset(dict(zip(parsed_ids, parsed_jsons)))

    def get_mbereads(self, ids):
        parsed_ids = list(map(lambda x: f'be_read_{x}', ids))
        cache_res = self.conn.mget(parsed_ids)
        res = list(map(lambda x: json_util.loads(x.decode('utf-8')) if x is not None else None, cache_res))
        return res, np.argwhere(np.array(res) == None).reshape(-1), np.argwhere(np.array(res) != None).reshape(-1)

    def set_mbereads(self, ids, jsons):
        parsed_ids = list(map(lambda x: f'be_read_{x}', ids))
        parsed_jsons = list(map(lambda x: json_util.dumps(x), jsons))
        self.conn.mset(dict(zip(parsed_ids, parsed_jsons)))

    def get_mpopularranks(self, ids):
        parsed_ids = list(map(lambda x: f'popular_rank_{x}', ids))
        cache_res = self.conn.mget(parsed_ids)
        res = list(map(lambda x: json_util.loads(x.decode('utf-8')) if x is not None else None, cache_res))
        return res, np.argwhere(np.array(res) == None).reshape(-1), np.argwhere(np.array(res) != None).reshape(-1)

    def set_mpopularranks(self, ids, jsons):
        parsed_ids = list(map(lambda x: f'popular_rank_{x}', ids))
        parsed_jsons = list(map(lambda x: json_util.dumps(x), jsons))
        self.conn.mset(dict(zip(parsed_ids, parsed_jsons)))
