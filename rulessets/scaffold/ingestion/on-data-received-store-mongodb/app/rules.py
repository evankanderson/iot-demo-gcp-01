from krules_core.base_functions import *

from krules_core import RuleConst as Const

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

from krules_core.providers import results_rx_factory, settings_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

from krules_mongodb import WithDatabase, WithCollection
from pymongo import IndexModel, HASHED
from dateutil.parser import parse

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

mongodb_settings = subjects_redis_storage_settings = settings_factory() \
        .get("scaffold").get("ingestion").get("mongodb")

rulesdata = [

    """
    Store received data on MongoDb
    """,
    {
        rulename: "on-data-received-store-mongodb",
        subscribe_to: "data-received",
        ruledata: {
            processing: [
                WithDatabase(mongodb_settings["database"]),
                WithCollection("data-received", indexes=[IndexModel([("deviceid", HASHED)])], capped=True, size=1000000,
                               exec_func=lambda c, self:
                                   c.insert_one({
                                       "deviceid": self.subject.name,
                                       "received_at": parse(self.payload["receivedAt"]),
                                       "data": self.payload["data"],
                                   }),
                               ),
            ],
        },
    },

]