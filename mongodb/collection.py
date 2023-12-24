import time
from pymongo import MongoClient


class Collection:
    @classmethod
    def get_current_timestamp(cls):
        return str(round(time.time() * 1000))


class MongoConn:
    @classmethod
    def connect(cls):
        return MongoClient('localhost', 60000)


class MongoDatabase:
    @classmethod
    def database(cls):
        return MongoConn.connect().demo
