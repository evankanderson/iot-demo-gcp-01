from krules_core.base_functions import *

from krules_core import RuleConst as Const

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

# import pprint
# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
results_rx_factory().subscribe(
    on_next=publish_results_all,
)
# results_rx_factory().subscribe(
#     on_next=publish_results_errors,
# )

rulesdata = [

    """
    My wonderful rule description
    """,
    {
        rulename: "on-onboard-device-store-properties",
        subscribe_to: "onboard-device",
        ruledata: {
            filters: [
                CheckPayloadMatchOne("data"),
                CheckPayloadMatchOne("class"),
            ],
            processing: [
                FlushSubject(),
                SetSubjectProperties(lambda payload: payload["data"]),
                SetSubjectExtendedProperty("deviceclass", lambda payload: payload["class"]),
                SetSubjectProperty('status', 'READY'),
            ],
        },
    },

]