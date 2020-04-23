import os
import yaml
from pymongo import MongoClient
from bson import ObjectId

from krules_core.base_functions import RuleFunctionBase


def get_client():

    config_path = os.environ.get("MONGODB_CONFIG_PATH", "/krules/config/mongodb/config_krules_mongodb.yaml")
    mongo_config = yaml.load(open(config_path, "r"), Loader=yaml.FullLoader)

    # TODO
    # return MongoClient(
    #     **mongo_config['MONGODB_CONNECT_KWARGS']
    # )
    return MongoClient(mongo_config["CONNECTION_STRING"])

def get_dbname(dbinfo):  # TODO: generalize

    database_name = dbinfo.get("database", os.environ.get("MONGODB_DEFAULT_DATABASE", "krules"))
    database_prefix = os.environ.get("MONGODB_DATABASE_PREFIX", "")
    database = "%s%s" % (database_prefix, database_name)

    return database

class WithDatabase(RuleFunctionBase):

    def execute(self, database):

        dbinfo = self.payload.get('_mongodb', {})
        dbinfo['database'] = database
        self.payload['_mongodb'] = dbinfo


class WithCollection(RuleFunctionBase):

    def execute(self, collection, **kwargs):

        exec_func = kwargs.pop("exec_func", None)

        dbinfo = self.payload.get('_mongodb', {})
        db = get_client()[get_dbname(dbinfo)]
        if collection not in db.collection_names():
            indexes=[]
            if "indexes" in kwargs:
                indexes = kwargs.pop("indexes")
            db.create_collection(collection, **kwargs)
            if len(indexes):
                db[collection].create_indexes(indexes)
        dbinfo['collection'] = collection
        self.payload['_mongodb'] = dbinfo

        if exec_func is not None:
            exec_func(db[collection], self)


class MongoDBInsertOne(RuleFunctionBase):

    def execute(self, *args, **kwargs):

        dbinfo = self.payload.get('_mongodb', {})
        database = get_dbname(dbinfo)
        collection = dbinfo.get("collection", os.environ.get("MONGODB_DEFAULT_COLLECTION", "default"))
        get_client()[database][collection].insert_one(*args, **kwargs)


class MongoDBUpdateOne(RuleFunctionBase):

    def execute(self, *args, **kwargs):

        dbinfo = self.payload.get('_mongodb', {})
        database = get_dbname(dbinfo)
        collection = dbinfo.get("collection", os.environ.get("MONGODB_DEFAULT_COLLECTION", "default"))
        get_client()[database][collection].update_one(*args, **kwargs)


class MongoDBFind(RuleFunctionBase):

    def execute(self, query, func):

        dbinfo = self.payload.get('_mongodb', {})
        database = get_dbname(dbinfo)
        collection = dbinfo.get("collection", os.environ.get("MONGODB_DEFAULT_COLLECTION", "default"))
        if callable(query):
            query = query(self)
        cursor = get_client()[database][collection].find(query)
        for c in cursor:
            func(c, self)


class MongoDBDeleteByIds(RuleFunctionBase):

    def execute(self, ids=[], payload_from="_ids"):

        dbinfo = self.payload.get('_mongodb', {})
        database = get_dbname(dbinfo)
        collection = dbinfo.get("collection", os.environ.get("MONGODB_DEFAULT_COLLECTION", "default"))

        ids.extend(self.payload.get(payload_from, []))
        res = get_client()[database][collection].delete_many({"_id": {"$in": [ObjectId(_id) for _id in ids]}})
        self.payload["{}_deleted_count".format(payload_from)] = res.deleted_count


