from datetime import datetime
import os

from dateutil.parser import parse
from app_functions.mongodb import set_client as set_mongodb_client
from app_functions.mongodb import WithDatabase, WithCollection, MongoDBFind, MongoDBDeleteByIds, MongoDBBulkWrite

from krules_core.base_functions import *

from krules_core import RuleConst as Const
from pymongo import IndexModel, TEXT, MongoClient

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

from krules_core.providers import results_rx_factory, settings_factory, message_router_factory, subject_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

# import pprint
# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
# results_rx_factory().subscribe(
#     on_next=publish_results_all,
# )
results_rx_factory().subscribe(
    on_next=publish_results_errors,
)
# results_rx_factory().subscribe(
#     on_next=lambda result: publish_results_filtered(result, "$.rule_name", "on-schedule-received")
# )

# results_rx_factory().subscribe(
#     on_next=lambda result: publish_results_filtered(result, "$..mongodb_bulk_api_result", lambda x: len(x))
# )

from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne

mongodb_settings = settings_factory().get("apps").get("mongodb")

DATABASE = os.environ.get("MONGODB_DATABASE", mongodb_settings.get("database"))
COLLECTION = os.environ.get("MONGODB_COLLECTION")

INDEXES = [IndexModel([("message", TEXT), ("subject", TEXT)])]
set_mongodb_client(
    MongoClient(*mongodb_settings.get("client_args", ()), **mongodb_settings.get("client_kwargs", {}))
)

rulesdata = [

    """
    Store schedule info (no replace)
    """,
    {
        rulename: "on-schedule-received-no-replace",
        subscribe_to: "schedule-message",
        ruledata: {
            filters: [
                IsFalse(lambda payload: payload.get("replace", False))
            ],
            processing: [
                WithDatabase(DATABASE),
                WithCollection(COLLECTION, indexes=INDEXES,
                               exec_func=lambda c, self: (
                                   c.insert_one({
                                       "message": self.payload["message"],
                                       "subject": self.payload["subject"],
                                       "payload": self.payload["payload"],
                                       "_when": parse(self.payload["when"])
                                   }))
                               )
            ]
        },
    },

    """
    Store schedule info
    """,
    {
        rulename: "on-schedule-received",
        subscribe_to: "schedule-message",
        ruledata: {
            filters: [
                IsTrue(lambda payload: payload.get("replace", False))
            ],
            processing: [
                WithDatabase(DATABASE),
                WithCollection(COLLECTION, indexes=INDEXES),
                MongoDBBulkWrite(lambda payload: [
                                 UpdateOne({
                                     "message": payload["message"],
                                     "subject": payload["subject"],
                                 }, {"$set": {
                                     "message": payload["message"],
                                     "subject": payload["subject"],
                                     "payload": payload["payload"],
                                     "_when": parse(payload["when"])
                                 }}, upsert=True)])
            ]
        },
    },
    """
    Do schedules
    """,
    {
        rulename: "on-tick-do-schedules",
        subscribe_to: "krules.heartbeat",
        ruledata: {
            processing: [
                SetPayloadProperty("_ids", []),
                WithDatabase(DATABASE),
                WithCollection(COLLECTION, indexes=INDEXES),
                MongoDBFind(
                    lambda self: {"_when": {"$lt": datetime.now()}},  # query
                    lambda x, self: (  # foreach
                        message_router_factory().route(x["message"],
                                                       subject_factory(x["subject"]),
                                                       x["payload"]),
                        self.payload["_ids"].append(str(x["_id"]))
                    ),
                ),
                MongoDBDeleteByIds(payload_from="_ids")
            ]
        }
    },

]