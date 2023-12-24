import pandas as pd
from pymongo import InsertOne, DeleteOne, ReplaceOne, UpdateOne
from mongodb.query_manager import *
from mongodb.user import *
from mongodb.article import *
from mongodb.read import *
from mongodb.be_read import *
from mongodb.popular_rank import *
import numpy as np
import json


class MongoInit:
    def __init__(self):
        self.root_dir = '../data-generation/'
        self.user_path = 'user.dat'
        self.article_path = 'article.dat'
        self.read_path = 'read.dat'
        self.bulk_size = 10000
        self.bulk_size_read = 50000

    def init_user(self):
        print('Initializing user collection...\n')
        user_file = open(self.root_dir + self.user_path, 'r')
        bulk_counter, bulk_dict = 0, {'Beijing': [], 'Hong Kong': []}
        for line in user_file.readlines():
            bulk_counter += 1
            doc = json.loads(line)
            bulk_dict[doc['region']] += [InsertOne(doc)]
            if bulk_counter == self.bulk_size:
                User.bulk_write(bulk_dict)
                bulk_counter = 0
                bulk_dict['Beijing'], bulk_dict['Hong Kong'] = [], []
        if bulk_counter > 0:
            User.bulk_write(bulk_dict)
        user_file.close()

    def init_article(self):
        print('Initializing article collection...\n')
        article_file = open(self.root_dir + self.article_path, 'r')
        bulk_counter, bulk_dict = 0, {'science': [], 'technology': []}
        for line in article_file.readlines():
            bulk_counter += 1
            doc = json.loads(line)
            bulk_dict[doc['category']] += [InsertOne(doc)]
            if bulk_counter == self.bulk_size:
                Article.bulk_write(bulk_dict)
                bulk_counter = 0
                bulk_dict['science'], bulk_dict['technology'] = [], []
        if bulk_counter > 0:
            Article.bulk_write(bulk_dict)
        article_file.close()

    def init_read(self):
        print('Initializing read collection...\n')
        read_file = open(self.root_dir + self.read_path, 'r')
        bulk_counter, bulk_list, uids = 0, [], []
        for line in read_file.readlines():
            bulk_counter += 1
            doc = json.loads(line)
            uids += [doc['uid']]
            bulk_list += [InsertOne(doc)]
            if bulk_counter == self.bulk_size_read:
                regions = QueryManager.query_user({'uid': {'$in': uids}}, {'uid': 1, 'region': 1}, cache=False)
                regions = dict(map(lambda x: (x['uid'], x['region']), regions))
                regions = list(map(lambda x: regions[x], uids))
                beijing_index = np.argwhere(np.array(regions) == 'Beijing').reshape(-1)
                hk_index = np.argwhere(np.array(regions) == 'Hong Kong').reshape(-1)
                Read.bulk_write({'Beijing': list(np.array(bulk_list)[beijing_index]),
                                 'Hong Kong': list(np.array(bulk_list)[hk_index])})
                bulk_counter, bulk_list, uids = 0, [], []
        if bulk_counter > 0:
            regions = QueryManager.query_user({'uid': {'$in': uids}}, {'uid': 1, 'region': 1}, cache=False)
            regions = dict(map(lambda x: (x['uid'], x['region']), regions))
            regions = list(map(lambda x: regions[x], uids))
            beijing_index = np.argwhere(np.array(regions) == 'Beijing').reshape(-1)
            hk_index = np.argwhere(np.array(regions) == 'Hong Kong').reshape(-1)
            Read.bulk_write({'Beijing': list(np.array(bulk_list)[beijing_index]),
                             'Hong Kong': list(np.array(bulk_list)[hk_index])})
        read_file.close()

    def init_be_read(self):
        print('Initializing be-read collection...\n')
        bulk_counter, bulk_list, bulk_aids = 0, [], []
        aids = QueryManager.query_article({}, {'aid': 1}, cache=False)
        aids = set(map(lambda x: x['aid'], aids))
        res = QueryManager.query_read({'aid': {'$in': list(aids)}}, {'aid': 1, 'uid': 1}, cache=False)
        read_num, read_list = self.iterate_query_be_read(res)
        res = QueryManager.query_read({'aid': {'$in': list(aids)}, "commentOrNot": '1'}, {'aid': 1, 'uid': 1}, cache=False)
        comment_num, comment_list = self.iterate_query_be_read(res)
        res = QueryManager.query_read({'aid': {'$in': list(aids)}, "agreeOrNot": '1'}, {'aid': 1, 'uid': 1}, cache=False)
        agree_num, agree_list = self.iterate_query_be_read(res)
        res = QueryManager.query_read({'aid': {'$in': list(aids)}, "shareOrNot": '1'}, {'aid': 1, 'uid': 1}, cache=False)
        share_num, share_list = self.iterate_query_be_read(res)
        for aid in aids:
            bulk_counter += 1
            bulk_aids += [aid]
            doc = {
                'id': f'br{aid}',
                'timestamp': str(Collection.get_current_timestamp()),
                'aid': aid,
                'readNum': read_num[aid],
                'readUidList': read_list[aid],
                'commentNum': comment_num[aid],
                'commentUidList': comment_list[aid],
                'agreeNum': agree_num[aid],
                'agreeUidList': agree_list[aid],
                'shareNum': share_num[aid],
                'shareUidList': share_list[aid]
            }
            bulk_list += [InsertOne(doc)]
            if bulk_counter == self.bulk_size:
                categories = QueryManager.query_article({'aid': {'$in': bulk_aids}}, {'category': 1}, cache=False)
                categories = list(map(lambda x: x['category'], categories))
                science_index = np.argwhere(np.array(categories) == 'science').reshape(-1)
                tech_index = np.argwhere(np.array(categories) == 'technology').reshape(-1)
                BeRead.bulk_write({'science': list(np.array(bulk_list)[science_index]),
                                   'technology': list(np.array(bulk_list)[tech_index])})
                bulk_counter, bulk_list, bulk_aids = 0, [], []
        if bulk_counter > 0:
            categories = QueryManager.query_article({'aid': {'$in': bulk_aids}}, {'category': 1}, cache=False)
            categories = list(map(lambda x: x['category'], categories))
            science_index = np.argwhere(np.array(categories) == 'science').reshape(-1)
            tech_index = np.argwhere(np.array(categories) == 'technology').reshape(-1)
            BeRead.bulk_write({'science': list(np.array(bulk_list)[science_index]),
                               'technology': list(np.array(bulk_list)[tech_index])})

    def iterate_query_be_read(self, res):
        out_dict = {}
        for i in res:
            if not i['aid'] in out_dict:
                out_dict[i['aid']] = [i['uid']]
            else:
                out_dict[i['aid']] += [i['uid']]
        out_num = dict(map(lambda x: (x[0], str(len(x[1]))), out_dict.items()))
        out_list = dict(map(lambda x: (x[0], list(set(x[1]))), out_dict.items()))
        return out_num, out_list

    def init_popular_rank(self):
        print('Initializing popular-rank collection...\n')
        read_file = open(self.root_dir + self.read_path, 'r')
        time_reads = {'daily': {}, 'weekly': {}, 'monthly': {}}
        for line in read_file.readlines():
            read = json.loads(line)
            aid = read['aid']
            t = ReadTime(read['timestamp'])
            for g in time_reads.keys():
                if not t.read_timestamp[g] in time_reads[g]:
                    time_reads[g][t.read_timestamp[g]] = {}
                if not aid in time_reads[g][t.read_timestamp[g]]:
                    time_reads[g][t.read_timestamp[g]][aid] = 1
                else:
                    time_reads[g][t.read_timestamp[g]][aid] += 1

        prid = 0
        insert_dict = {'daily': [], 'weekly': [], 'monthly': []}
        for g in time_reads.keys():
            for time in time_reads[g]:
                time_reads[g][time] = sorted(time_reads[g][time].items(), key=lambda x: x[1], reverse=True)
                time_reads[g][time] = list(map(lambda x: x[0], time_reads[g][time]))
                doc = {
                    'id': f'pr{prid}',
                    'temporalGranularity': g,
                    'articleAidList': time_reads[g][time]
                }
                if g == 'daily':
                    doc['timestamp'] = DateToTimestamp.day_tmp(time)
                elif g == 'weekly':
                    doc['timestamp'] = DateToTimestamp.week_tmp(time)
                elif g == 'monthly':
                    doc['timestamp'] = DateToTimestamp.month_tmp(time)
                insert_dict[g] += [InsertOne(doc)]
                prid += 1

        PopularRank.write(insert_dict)

    def init_all(self):
        self.init_user()
        self.init_article()
        self.init_read()
        self.init_be_read()
        self.init_popular_rank()


if __name__ == '__main__':
    init = MongoInit()
    init.init_all()

