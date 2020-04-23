from dependency_injector import providers as providers
import jsonpath_rw_ext as jp

from krules_core.arg_processors import processors
from krules_core.providers import (
    subject_storage_factory,
    settings_factory
)
import os


def init():
    pass
    # This is an inmemory database and it is not persistent
    # you probably want to comment out this configuration and enable a more appropriate one
    # Redis subjects storage support
    subjects_redis_storage_settings = settings_factory() \
        .get("subjects-backends") \
        .get("redis")
    from redis_subjects_storage import storage_impl as redis_storage_impl

    subject_storage_factory.override(
        providers.Factory(
            lambda x: redis_storage_impl.SubjectsRedisStorage(x, subjects_redis_storage_settings.get("url"))
        )
    )

    # MongoDB subjects storage support
    # subjects_mongodb_storage_settings = settings_factory() \
    #     .get("subjects-backends") \
    #     .get("mongodb")
    #
    # from mongodb_subjects_storage import storage_impl as mongo_storage_impl
    #
    # client_args = subjects_mongodb_storage_settings["client_args"]
    # client_kwargs = subjects_mongodb_storage_settings["client_kwargs"]
    # database = subjects_mongodb_storage_settings["database"]
    # collection = subjects_mongodb_storage_settings.get("collection", "subjects")
    # use_atomic_ops_collection = subjects_mongodb_storage_settings.get("use_atomic_ops_collection", False)
    # atomic_ops_collection_size = subjects_mongodb_storage_settings.get("atomic_ops_collection_size", 5242880)
    # atomic_ops_collection_max = subjects_mongodb_storage_settings.get("atomic_ops_collection_max", 1000)
    #
    # subject_storage_factory.override(
    #     providers.Factory(
    #         lambda x: mongo_storage_impl.SubjectsMongoStorage(x, database, collection,
    #                                                           client_args=client_args, client_kwargs=client_kwargs,
    #                                                           use_atomic_ops_collection=use_atomic_ops_collection,
    #                                                           atomic_ops_collection_size=atomic_ops_collection_size,
    #                                                           atomic_ops_collection_max=atomic_ops_collection_max
    #                                                           ))
    # )


class JPPayloadMatchBase:

    def __init__(self, expr):
        self._expr = expr

    @classmethod
    def interested_in(cls, arg):
        return isinstance(arg, cls)


# class JPMatch(JPPayloadMatchBase):
#
#     @staticmethod
#     def process(instance, arg):
#         return jp.match(arg._expr, instance.payload)


class jp_match1(JPPayloadMatchBase):

    @staticmethod
    def process(instance, arg):
        return jp.match1(arg._expr, instance.payload)


processors.append(jp_match1)
# processors.append(JPMatch)
