from app_functions import WebsocketDevicePublishMessage, WebsocketNotificationEventClass
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
    tempc websocket notifier
    """,
    {
        rulename: "on-tempc-changed-websocket-notifier",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("tempc"),
            ],
            processing: [
                WebsocketDevicePublishMessage(lambda payload: {
                    "value": payload.get("value")
                }),
            ],
        },
    },

    """
    On status NORMAL notify
    """,
    {
        rulename: "on-temp-status-back-to-normal-websocket-notifier",
        subscribe_to: "temp-status-back-to-normal",
        ruledata: {
            processing: [
                WebsocketDevicePublishMessage({
                    "event": "Temp status back to normal! ",
                    "event_class": WebsocketNotificationEventClass.NORMAL,
                }),
            ],
        },
    },

    """
    Status COLD or OVERHEATED
    """,
    {
        rulename: "on-temp-status-bad-websocket-notifier",
        subscribe_to: "temp-status-bad",
        ruledata: {
            processing: [
                WebsocketDevicePublishMessage(lambda self: {
                    "event": "*{}* ({}°C)".format(
                        self.payload.get("status"), self.subject.get("tempc")
                    ),
                    "event_class": WebsocketNotificationEventClass.WARNING,
                }),
            ],
        },
    },

    """
    Recheck
    """,
    {
        rulename: "on-temp-status-recheck-websocket-notifier",
        subscribe_to: "temp-status-still-bad",
        ruledata: {
            processing: [
                WebsocketDevicePublishMessage(lambda payload: {
                    "event": "...still *{}* from {} secs".format(
                        payload.get("status"),
                        payload.get("seconds"),
                    ),
                    "event_class": WebsocketNotificationEventClass.CRITICAL,
                }),
            ],
        },
    },
]
