from mongodb.collection import *


class User(Collection):
    @classmethod
    def user(cls):
        return {'Beijing': MongoDatabase.database().user_beijing,
                'Hong Kong': MongoDatabase.database().user_hong_kong}

    @classmethod
    def bulk_write(cls, bulk_dict):
        if bulk_dict['Beijing']:
            User.user()['Beijing'].bulk_write(bulk_dict['Beijing'], ordered=True)
        if bulk_dict['Hong Kong']:
            User.user()['Hong Kong'].bulk_write(bulk_dict['Hong Kong'], ordered=True)

    @classmethod
    def delete(cls, uid_dict):
        User.user()['Beijing'].bulk_write(uid_dict['Beijing'], ordered=True)
        User.user()['Hong Kong'].bulk_write(uid_dict['Hong Kong'], ordered=True)
