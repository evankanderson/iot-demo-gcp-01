from krules_core.base_functions import *

from krules_core import RuleConst as Const
import os

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

from krules_core.providers import results_rx_factory, settings_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

from app_functions.mongodb import WithDatabase, WithCollection
from app_functions.mongodb import set_client as set_mongodb_client
from pymongo import IndexModel, HASHED, MongoClient
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

mongodb_settings = settings_factory().get("apps").get("mongodb")
set_mongodb_client(
    MongoClient(*mongodb_settings.get("client_args", ()), **mongodb_settings.get("client_kwargs", {}))
)

DATABASE = os.environ.get("MONGODB_DATABASE", mongodb_settings.get("database"))
COLLECTION = os.environ.get("MONGODB_COLLECTION", mongodb_settings.get("collection"))

rulesdata = [

    """
    Store received data on MongoDb
    """,
    {
        rulename: "on-data-received-store-mongodb",
        subscribe_to: "data-received",
        ruledata: {
            processing: [
                WithDatabase(DATABASE),
                WithCollection(COLLECTION,
                               indexes=[IndexModel([("deviceid", HASHED)])],
                               capped=True, size=1000000,
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
