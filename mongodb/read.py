from mongodb.collection import *


class Read(Collection):
    @classmethod
    def read(cls):
        return {'Beijing': MongoDatabase.database().read_beijing,
                'Hong Kong': MongoDatabase.database().read_hong_kong}

    @classmethod
    def bulk_write(cls, bulk_dict):
        if bulk_dict['Beijing']:
            Read.read()['Beijing'].bulk_write(list(bulk_dict['Beijing']), ordered=True)
        if bulk_dict['Hong Kong']:
            Read.read()['Hong Kong'].bulk_write(list(bulk_dict['Hong Kong']), ordered=True)
