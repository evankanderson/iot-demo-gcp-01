from krules_core.base_functions import *

from krules_core import RuleConst as Const, TopicsDefault
import os

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

from krules_core.providers import results_rx_factory, settings_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered
from app_functions.mongodb import set_client as set_mongodb_client
from app_functions.mongodb import WithDatabase, WithCollection, MongoDBInsertOne
from dateutil.parser import parse
from pymongo import IndexModel, HASHED, MongoClient

# import pprint
# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
# results_rx_factory().subscribe(
#     on_next=publish_results_all,
# )
# results_rx_factory().subscribe(
#     on_next=publish_results_errors,
# )

mongodb_settings = settings_factory().get("apps").get("mongodb")
set_mongodb_client(
    MongoClient(*mongodb_settings.get("client_args", ()), **mongodb_settings.get("client_kwargs", {}))
)

DATABASE = os.environ.get("MONGODB_DATABASE")
COLLECTION_RAW = os.environ.get("MONGODB_COLLECTION_RAW")
COLLECTION_ERRORS = os.environ.get("MONGODB_COLLECTION_ERRORS")

rulesdata = [

    """
    Save raw data
    """,
    {
        rulename: "mongo-store-full-data",
        subscribe_to: TopicsDefault.RESULTS,
        ruledata: {
            processing: [
                WithDatabase(DATABASE),
                WithCollection(COLLECTION_RAW,
                               indexes=[IndexModel([("origin_id", HASHED)])],
                               capped=True, size=1000000),
                SetPayloadProperty("origin_id", lambda payload: payload["payload"]["_event_info"]["Originid"]),
                SetPayloadProperty("time", lambda payload: parse(payload["payload"]["_event_info"]["Time"])),
                MongoDBInsertOne(lambda payload: payload),
            ],
        },
    },

    """
    Errors in his own collection
    """,
    {
        rulename: "mongo-store-errors",
        subscribe_to: TopicsDefault.RESULTS,
        ruledata: {
            filters: [
                IsTrue(lambda payload: payload["got_errors"])
            ],
            processing: [
                WithDatabase(DATABASE),
                WithCollection(COLLECTION_ERRORS,
                               indexes=[IndexModel([("origin_id", HASHED)])],
                               capped=True, size=1000000),
                SetPayloadProperty("origin_id", lambda payload: payload["payload"]["_event_info"]["Originid"]),
                SetPayloadProperty("time", lambda payload: parse(payload["payload"]["_event_info"]["Time"])),
                CheckPayloadMatchOne("*[?(@.exception)]", payload_dest="function"),
                MongoDBInsertOne(lambda payload: {
                    "origin_id": payload["origin_id"],
                    "time": payload["time"],
                    "message": payload["message"],
                    "subject": payload["subject"],
                    "rule_name": payload["rule_name"],
                    "function": payload["function"],
                }),
            ],
        },
    },
]
