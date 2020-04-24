from datetime import datetime, timedelta

from dateutil.parser import parse

from app_functions import Schedule
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
results_rx_factory().subscribe(
    on_next=publish_results_all,
)
# results_rx_factory().subscribe(
#     on_next=publish_results_errors,
# )

rulesdata = [

    """
    On status NORMAL notify
    """,
    {
        rulename: "on-temp-status-back-to-normal",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                IsTrue(lambda payload: payload["value"] == "NORMAL"),
                IsFalse(lambda payload: payload["value"] in (None, ))
            ],
            processing: [
                Route(message="temp-status-back-to-normal",
                      dispatch_policy=DispatchPolicyConst.DIRECT),
                SetSubjectPropertySilently("lastTempStatusChanged", datetime.now().isoformat())
            ],
        },
    },

    """
    Status COLD or OVERHEATED schedule a new check
    """,
    {
        rulename: "on-temp-status-bad",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                IsTrue(lambda payload: payload["value"] in ("COLD", "OVERHEATED")),
            ],
            processing: [
                Route(message="temp-status-bad", payload=lambda self: {
                    "tempc": str(self.subject.tempc),
                    "status": self.payload.get("value")
                }, dispatch_policy=DispatchPolicyConst.DIRECT),
                SetSubjectProperty("m_lastTempStatusChanged", _(lambda _: datetime.now().isoformat())),
                Schedule(message="temp-status-recheck",
                         payload=lambda payload: {"old_value": payload["value"]},
                         when=lambda _: (datetime.now()+timedelta(seconds=30)).isoformat()),
            ],
        },
    },

    """
    Recheck
    """,
    {
        rulename: "on-temp-status-recheck",
        subscribe_to: "temp-status-recheck",
        ruledata: {
            filters: [
                IsTrue(lambda self: self.payload.get("old_value") == self.subject.temp_status)
            ],
            processing: [
                Route(message="temp-status-still-bad", payload=_(lambda _self: {
                    "status": _self.payload.get("old_value"),
                    "seconds": (datetime.now() - parse(_self.subject.m_lastTempStatusChanged)).seconds
                }), dispatch_policy=DispatchPolicyConst.DIRECT),
                Schedule(message="temp-status-recheck",
                         payload=lambda payload: {"old_value": payload["old_value"]},
                         when=lambda _: (datetime.now()+timedelta(seconds=15)).isoformat()),
            ],
        },
    },

]
