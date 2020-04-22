from krules_core.base_functions import *

from krules_core import RuleConst as Const, TopicsDefault

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered
from krules_mongodb import WithDatabase, WithCollection, MongoDBInsertOne
from dateutil.parser import parse
from pymongo import IndexModel, HASHED

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

DBNAME = "kr-dev-03"

rulesdata = [

    """
    Save raw data
    """,
    {
        rulename: "mongo-store-full-data",
        subscribe_to: TopicsDefault.RESULTS,
        ruledata: {
            processing: [
                WithDatabase(DBNAME),
                WithCollection("metrics", indexes=[IndexModel([("origin_id", HASHED)])], capped=True, size=1000000),
                SetPayloadProperty("origin_id", lambda payload: payload["payload"]["_event_info"]["Originid"]),
                SetPayloadProperty("time", lambda payload: parse(payload["payload"]["_event_info"]["Time"])),
                MongoDBInsertOne(lambda payload: payload),
            ],
        },
    },

]