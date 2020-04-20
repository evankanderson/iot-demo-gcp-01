from dependency_injector import providers as providers
from krules_core.providers import subject_storage, subject_storage_factory
import jsonpath_rw_ext as jp
from krules_core.arg_processors import processors


def init():

    # This is an inmemory database and it is not persistent
    subject_storage_factory.override(
        providers.Factory(lambda x: subject_storage(x, ":memory:"))
    )

    # # Redis subjects storage support
    import os
    from redis_subjects_storage import storage_impl
    subject_storage_redis = providers.Factory(storage_impl.SubjectsRedisStorage)

    subject_storage_factory.override(
        providers.Factory(lambda x: subject_storage_redis(x, os.environ["KRULES_SUBJECTS_REDIS_URL"]))
    )

    # # MongoDB subjects storage support
    # import yaml, os
    # subjects_mongodb_storage_settings = yaml.load(
    #     open("/krules/config/mongodb/config_subjects_mongodb.yaml", "r"), Loader=yaml.FullLoader)
    #
    # from mongodb_subjects_storage import storage_impl
    # subject_storage.override(
    #     providers.Factory(storage_impl.SubjectsMongoStorage)
    # )
    #
    # client_args = subjects_mongodb_storage_settings["client_args"]
    # client_kwargs = subjects_mongodb_storage_settings["client_kwargs"]
    # if "username" not in client_kwargs:
    #     client_kwargs["username"] = os.environ.get("KRULES_SUBJECTS_MONGODB_USERNAME").strip()
    # if "password" not in client_kwargs:
    #     client_kwargs["password"] = os.environ.get("KRULES_SUBJECTS_MONGODB_PASSWORD").strip()
    # database = subjects_mongodb_storage_settings["database"]
    # collection = subjects_mongodb_storage_settings.get("collection", "subjects")
    #
    # subject_storage_factory.override(
    #     providers.Factory(
    #         lambda x: subject_storage(x, database, collection,
    #                                   client_args=client_args, client_kwargs=client_kwargs,
    #                                   use_atomic_ops_collection=True))
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


class JPMatchOne(JPPayloadMatchBase):

    @staticmethod
    def process(instance, arg):
        return jp.match1(arg._expr, instance.payload)


processors.append(JPMatchOne)
# processors.append(JPMatch)
