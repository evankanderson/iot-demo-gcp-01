from datetime import datetime

from app_functions import B64Decode
from krules_core.base_functions import *

from krules_core import RuleConst as Const

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING


from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

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


rulesdata = [

    """
    Just emit "data-received" event
    Data should be handled by application specific logic
    """,
    {
        rulename: "on-data-received-propagate",
        subscribe_to: "com.google.cloud.pubsub.topic.publish",
        ruledata: {
            processing: [
                SetSubjectPropertySilently("lastSeen", datetime.now().isoformat()),
                B64Decode(
                        source=lambda payload: payload["message"]["data"],
                        payload_dest="data"
                        ),
                Route("data-received",                                  # message
                      lambda payload: payload["data"].pop("deviceid"),  # subject
                      lambda payload: {                                 # payload
                          "receivedAt": payload["_event_info"]["Time"],
                          "data": payload["data"]
                      }),
            ],
        },
    },

]