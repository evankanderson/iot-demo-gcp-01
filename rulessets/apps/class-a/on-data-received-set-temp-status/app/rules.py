from krules_core.base_functions import *

from krules_core import RuleConst as Const, messages

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
# results_rx_factory().subscribe(
#     on_next=publish_results_all,
# )
results_rx_factory().subscribe(
    on_next=lambda x: publish_results_filtered(x, "$.rule_name", "temp-status-propagate")
)
results_rx_factory().subscribe(
    on_next=publish_results_errors,
)

rulesdata = [

    """
    Store temp property
    """,
    {
        rulename: "on-data-received-store-temp",
        subscribe_to: "data-received",
        ruledata: {
            filters: [
                IsTrue(lambda payload: "tempc" in payload["data"])
            ],
            processing: [
                SetSubjectProperty("tempc", lambda payload: payload["data"]["tempc"])
            ],
        },
    },

    """
    Set temp_status COLD 
    """,
    {
        rulename: "on-tempc-changed-check-cold",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("tempc"),
                IsTrue(lambda self:
                       float(self.payload.get("value")) < float(self.subject.get("temp_min"))
                       ),
            ],
            processing: [
                SetSubjectProperty("temp_status", "COLD"),
            ],
        }
    },

    """
    Set temp_status NORMAL 
    """,
    {
        rulename: "on-tempc-changed-check-normal",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("tempc"),
                IsTrue(lambda self:
                       float(self.subject.get("temp_min")) <= float(self.payload.get("value")) < float(self.subject.get("temp_max"))
                       ),
            ],
            processing: [
                SetSubjectProperty("temp_status", "NORMAL"),
            ],
        }
    },

    """
    Set temp_status OVERHEATED 
    """,
    {
        rulename: "on-tempc-changed-check-overheated",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("tempc"),
                IsTrue(lambda self:
                       float(self.payload.get("value")) >= float(self.subject.get("temp_max"))
                       )
            ],
            processing: [
                SetSubjectProperty("temp_status", "OVERHEATED"),
            ],
        }
    },

    """
    Since we have already intercepted the prop changed event inside the container we need to send it out 
    explicitily (both tempc and temp_status)
    """,
    {
        rulename: "temp-status-propagate",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged(lambda x: x in ("temp_status",)),
            ],
            processing: [
                Route(dispatch_policy=DispatchPolicyConst.DIRECT)
            ]
        },
    },
]
