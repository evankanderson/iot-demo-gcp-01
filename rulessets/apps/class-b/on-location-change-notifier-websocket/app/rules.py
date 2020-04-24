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
# results_rx_factory().subscribe(
#     on_next=publish_results_all,
# )
results_rx_factory().subscribe(
    on_next=publish_results_errors,
)

rulesdata = [

    """
    Send all coords variations
    """,
    {
        rulename: "on-coords-changed-notify-websocket",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("coords"),
            ],
            processing: [
                WebsocketDevicePublishMessage(lambda payload: {
                    "value": payload["value"],
                }),
            ]
        }
    },

    """
    Send location (cheering)
    """,
    {
        rulename: "on-location-changed-notify-websocket-cheering",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("location"),
                IsTrue(lambda payload: payload["old_value"] is None)
            ],
            processing: [
                WebsocketDevicePublishMessage(lambda payload: {
                    "event": payload["value"],
                    "event_class": WebsocketNotificationEventClass.CHEERING,
                }),
            ]
        }
    },

    """
    Send location (normal)
    """,
    {
        rulename: "on-location-changed-notify-websocket-normal",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("location"),
                IsFalse(lambda payload: payload["old_value"] is None)
            ],
            processing: [
                WebsocketDevicePublishMessage(lambda payload: {
                    "event": payload["value"],
                    "event_class": WebsocketNotificationEventClass.NORMAL,
                }),
            ]
        }
    },

]