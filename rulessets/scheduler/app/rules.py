from datetime import datetime

from dateutil.parser import parse
from app_functions import mongodb as mongodb_functions

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
# results_rx_factory().subscribe(
#     on_next=publish_results_errors,
# )
results_rx_factory().subscribe(
    on_next=lambda result: publish_results_filtered(result, "$.._ids_deleted_count", lambda x: x and x > 0)
)

INDEXES = [IndexModel([("message", TEXT), ("subject", TEXT)])]
mongodb_settings = settings_factory().get("apps").get("scheduler").get("mongodb")
mongodb_functions.set_client(
    MongoClient(*mongodb_settings.get("client_args", ()), **mongodb_settings.get("client_kwargs", {}))
)

rulesdata = [

    """
    Store schedule info
    """,
    {
        rulename: "on-schedule-received",
        subscribe_to: "schedule-message",
        ruledata: {
            processing: [
                mongodb_functions.WithDatabase(mongodb_settings["database"]),
                mongodb_functions.WithCollection(mongodb_settings["collection"], indexes=INDEXES,
                               exec_func=lambda c, payload: (
                                       payload.get("replace") and c.delete_many({
                                           "message": payload["message"],
                                           "subject": payload["subject"],
                                       }),
                                       c.insert_one({
                                           "message": payload["message"],
                                           "subject": payload["subject"],
                                           "payload": payload["payload"],
                                           "_when": parse(payload["when"])
                                       })
                                   )
                               )
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
                mongodb_functions.WithDatabase(mongodb_settings["database"]),
                mongodb_functions.WithCollection(mongodb_settings["collection"], indexes=INDEXES),
                mongodb_functions.MongoDBFind(
                    lambda self: {"_when": {"$lt": datetime.now()}},  # query
                    lambda x, payload: (  # foreach
                        message_router_factory().route(x["message"],
                                                       subject_factory(x["subject"]),
                                                       x["payload"]),
                        payload["_ids"].append(str(x["_id"]))
                    ),
                ),
                mongodb_functions.MongoDBDeleteByIds(payload_from="_ids")
            ]
        }
    },

]
