from mongodb.collection import *


class Article(Collection):
    @classmethod
    def article(cls):
        return {'science': MongoDatabase.database().article_science,
                'technology': MongoDatabase.database().article_tech}

    @classmethod
    def bulk_write(cls, bulk_dict):
        if bulk_dict['science']:
            Article.article()['science'].bulk_write(bulk_dict['science'], ordered=True)
        if bulk_dict['technology']:
            Article.article()['technology'].bulk_write(bulk_dict['technology'], ordered=True)
