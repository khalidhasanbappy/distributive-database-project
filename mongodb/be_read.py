from mongodb.collection import *


class BeRead(Collection):
    @classmethod
    def be_read(cls):
        return {'science': MongoDatabase.database().be_read_science,
                'technology': MongoDatabase.database().be_read_tech}

    @classmethod
    def bulk_write(cls, bulk_dict):
        if bulk_dict['science']:
            BeRead.be_read()['science'].bulk_write(bulk_dict['science'], ordered=True)
        if bulk_dict['technology']:
            BeRead.be_read()['technology'].bulk_write(bulk_dict['technology'], ordered=True)
