from app_functions import WebsocketNotificationEventClass, WebsocketDevicePublishMessage
from krules_core.base_functions import *

from krules_core import RuleConst as Const, messages

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
# results_rx_factory().subscribe(
#     on_next=publish_results_all,
# )
results_rx_factory().subscribe(
    on_next=publish_results_errors,
)


rulesdata = [

    """
    Notify onboarded (READY)
    """,
    {
        rulename: "on-device-ready-notify-websocket",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                IsTrue(lambda payload: payload["value"] == "READY"),
            ],
            processing: [
                WebsocketDevicePublishMessage(lambda subject: {
                    "device_class": subject.get_ext("deviceclass"),
                    "status": subject.status,
                    "event": "Onboarded",
                    "event_class": WebsocketNotificationEventClass.CHEERING,
                })
            ],
        },
    },

    """
    Notify ACTIVE
    """,
    {
        rulename: "on-device-active-notify-websocket",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                IsTrue(lambda payload: payload["value"] == "ACTIVE"),
            ],
            processing: [
                WebsocketDevicePublishMessage({
                    "status": "ACTIVE",
                    "event": "Receiving data",
                    "event_class": WebsocketNotificationEventClass.NORMAL,
                })

            ],
        },
    },

    """
    Notify INACTIVE
    """,
    {
        rulename: "on-device-inactive-notify-websocket",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                IsTrue(lambda payload: payload["value"] == "INACTIVE"),
            ],
            processing: [
                WebsocketDevicePublishMessage({
                    "status": "INACTIVE",
                    "event": "No more data receiving",
                    "event_class": WebsocketNotificationEventClass.WARNING,
                })

            ],
        },
    },

]