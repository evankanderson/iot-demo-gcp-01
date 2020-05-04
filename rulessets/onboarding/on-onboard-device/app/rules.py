from krules_core.base_functions import *

from krules_core import RuleConst as Const

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

import pprint
results_rx_factory().subscribe(
    on_next=pprint.pprint
)
results_rx_factory().subscribe(
    on_next=publish_results_all,
)
# results_rx_factory().subscribe(
#     on_next=publish_results_errors,
# )

rulesdata = [

    """
    Set the basic properties of the device and the initial status as 'READY'
    The status will become 'ACTIVE' upon receipt of the first message
    """,
    {
        rulename: "on-onboard-device-store-properties",
        subscribe_to: "onboard-device",
        ruledata: {
            filters: [
                IsTrue(lambda payload: "data" in payload and "class" in payload),
            ],
            processing: [
                FlushSubject(),
                SetSubjectProperties(lambda payload: payload["data"]),
                SetSubjectExtendedProperty("deviceclass", lambda payload: payload["class"]),
                SetSubjectProperty('status', 'READY', muted=True),
            ],
        },
    },

]
