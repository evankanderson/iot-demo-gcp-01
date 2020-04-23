from krules_core.base_functions import *

from krules_core import RuleConst as Const, messages

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

import redis
import os

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


class NotificationEventClass(object):

    CHEERING = "cheering"
    WARNING = "warning"
    CRITICAL = "critical"
    NORMAL = "normal"


class WebsocketDevicePublishMessage(RuleFunctionBase):

    def execute(self, _payload):

        r = redis.StrictRedis.from_url(os.environ['REDIS_PUBSUB_ADDRESS'])
        r.publish(os.environ['WEBSOCKET_DEVICES_NOTIFICATION_RKEY'], json.dumps(
            {
                "device": self.subject.name,
                "payload": _payload
            }
        ))


rulesdata = [

    """
    Notify onboarded (READY)
    """,
    {
        rulename: "on-device-ready-notify-websocket",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadMatchOne("$.value", "READY"),
            ],
            processing: [
                WebsocketDevicePublishMessage(lambda subject: {
                    "device_class": subject.get_ext("deviceclass"),
                    "status": subject.status,
                    "event": "Onboarded",
                    "event_class": NotificationEventClass.CHEERING,
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
                CheckPayloadMatchOne("$.value",  "ACTIVE"),
            ],
            processing: [
                WebsocketDevicePublishMessage({
                    "status": "ACTIVE",
                    "event": "Receiving data",
                    "event_class": NotificationEventClass.NORMAL,
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
                CheckPayloadMatchOne("$.value",  "INACTIVE"),
            ],
            processing: [
                WebsocketDevicePublishMessage({
                    "status": "INACTIVE",
                    "event": "No more data receiving",
                    "event_class": NotificationEventClass.WARNING,
                })

            ],
        },
    },

]