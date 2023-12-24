from mongodb.config import *
from redis_cache.redis_utils import *


class QueryManager:
    @classmethod
    def query_user(self, query={}, field={}, cache=True):
        res_cache, res_db = [], []
        if 'uid' in query and cache == True:
            cache = Cache()
            uid = query['uid']
            if isinstance(uid, dict):
                uids = uid['$in']
            else:
                uids = [uid]
            res_cache, non_pos_cache, pos_cache = cache.get_musers(uids)
            if non_pos_cache.shape[0]:
                uids = list(np.array(uids)[non_pos_cache])
                query['uid'] = {'$in': uids}
                cols = list(User.user().values())
                res_db = list(cols[0].find(query, field)) + list(cols[1].find(query, field))
                if len(uids) != len(res_db):
                    return res_db
                cache.set_musers(uids, res_db)
            return list(np.array(res_cache)[pos_cache]) + res_db

        cols = list(User.user().values())
        return list(cols[0].find(query, field)) + list(cols[1].find(query, field)) + res_cache

    @classmethod
    def insert_user(self, user_dict):
        insert_dict = {'Beijing': [], 'Hong Kong': []}
        insert_dict[user_dict['region']] = [InsertOne(user_dict)]
        User.bulk_write(insert_dict)

    @classmethod
    def update_user(self, user_dict):
        uid = user_dict['uid']
        del user_dict['uid']
        cache = Cache()
        cache.delete_user(uid)
        update_dict = {'Beijing': [UpdateOne({'uid': uid}, {'$set': user_dict}, upsert=False)],
                       'Hong Kong': [UpdateOne({'uid': uid}, {'$set': user_dict}, upsert=False)]}
        User.bulk_write(update_dict)

    @classmethod
    def delete_user(self, user_dict):
        cache = Cache()
        cache.delete_user(user_dict['uid'])
        delete_dict = {'Beijing': [DeleteOne(user_dict)], 'Hong Kong': [DeleteOne(user_dict)]}
        User.delete(delete_dict)

    @classmethod
    def query_article(self, query={}, field={}, cache=True):
        res_cache, res_db = [], []
        if 'aid' in query and cache == True:
            cache = Cache()
            aid = query['aid']
            if isinstance(aid, dict):
                aids = aid['$in']
            else:
                aids = [aid]
            res_cache, non_pos_cache, pos_cache = cache.get_marticles(aids)
            if non_pos_cache.shape[0]:
                aids = list(np.array(aids)[non_pos_cache])
                query['aid'] = {'$in': aids}
                cols = list(Article.article().values())
                res_db = list(cols[0].find(query, field)) + list(cols[1].find(query, field))
                if len(aids) != len(res_db):
                    return res_db
                cache.set_marticles(aids, res_db)
            return list(np.array(res_cache)[pos_cache]) + res_db

        cols = list(Article.article().values())
        return list(cols[0].find(query, field)) + list(cols[1].find(query, field))

    @classmethod
    def query_read(self, query={}, field={}, cache=True):
        res_cache, res_db = [], []
        if 'id' in query and cache == True:
            cache = Cache()
            id = query['id']
            if isinstance(id, dict):
                ids = id['$in']
            else:
                ids = [id]
            res_cache, non_pos_cache, pos_cache = cache.get_mreads(ids)
            if non_pos_cache.shape[0]:
                ids = list(np.array(ids)[non_pos_cache])
                query['id'] = {'$in': ids}
                cols = list(Read.read().values())
                res_db = list(cols[0].find(query, field)) + list(cols[1].find(query, field))
                if len(ids) != len(res_db):
                    return res_db
                cache.set_mreads(ids, res_db)
            return list(np.array(res_cache)[pos_cache]) + res_db

        cols = list(Read.read().values())
        return list(cols[0].find(query, field)) + list(cols[1].find(query, field))

    @classmethod
    def query_be_read(self, query={}, field={}, cache=True):
        res_cache, res_db = [], []
        if 'id' in query and cache == True:
            cache = Cache()
            id = query['id']
            if isinstance(id, dict):
                ids = id['$in']
            else:
                ids = [id]
            res_cache, non_pos_cache, pos_cache = cache.get_mreads(ids)
            if non_pos_cache.shape[0]:
                ids = list(np.array(ids)[non_pos_cache])
                query['id'] = {'$in': ids}
                cols = list(BeRead.be_read().values())
                res_db = list(cols[0].find(query, field)) + list(cols[1].find(query, field))
                if len(ids) != len(res_db):
                    return res_db
                cache.set_mreads(ids, res_db)
            return list(np.array(res_cache)[pos_cache]) + res_db

        cols = list(BeRead.be_read().values())
        return list(cols[0].find(query, field)) + list(cols[1].find(query, field))

    @classmethod
    def query_popular_rank(self, query={}, field={}, cache=True):
        res_cache, res_db = [], []
        if 'id' in query and cache == True:
            cache = Cache()
            id = query['id']
            if isinstance(id, dict):
                ids = id['$in']
            else:
                ids = [id]
            res_cache, non_pos_cache, pos_cache = cache.get_mreads(ids)
            if non_pos_cache.shape[0]:
                ids = list(np.array(ids)[non_pos_cache])
                query['id'] = {'$in': ids}
                cols = list(PopularRank.popular_rank().values())
                res_db = list(cols[0].find(query, field)) \
                         + list(cols[1].find(query, field)) \
                         + list(cols[2].find(query, field))
                if len(ids) != len(res_db):
                    return res_db
                cache.set_mreads(ids, res_db)
            return list(np.array(res_cache)[pos_cache]) + res_db

        cols = list(PopularRank.popular_rank().values())
        return list(cols[0].find(query, field)) + list(cols[1].find(query, field)) + list(cols[2].find(query, field))

    @classmethod
    def query_join_read_user(self, query={}, field={}):
        cols = list(Read.read().values())
        read_res = list(cols[0].find(query, field)) + list(cols[1].find(query, field))
        uids = list(set(map(lambda x: x['uid'], read_res)))
        user_res = self.query_user({'uid': {'$in': uids}})
        users = dict(map(lambda x: (x['uid'], x), user_res))
        for read in read_res:
            read['user'] = users[read['uid']]
        return read_res

    @classmethod
    def query_join_user_read(self, query={}, field={}):
        cols = list(User.user().values())
        user_res = list(cols[0].find(query, field)) + list(cols[1].find(query, field))
        uids = list(set(map(lambda x: x['uid'], user_res)))
        read_res = self.query_read({'uid': {'$in': uids}})
        read_uid = {}
        for read in read_res:
            if not read['uid'] in read_uid:
                read_uid[read['uid']] = [read]
            else:
                read_uid[read['uid']] += [read]
        for user in user_res:
            user['reads'] = read_uid[user['uid']]
        return user_res
