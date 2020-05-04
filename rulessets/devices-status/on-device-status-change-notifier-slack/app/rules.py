import os

import requests

from krules_core.base_functions import *

from krules_core import RuleConst as Const, messages
from krules_core.base_functions.misc import PyCall

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

from krules_core.providers import results_rx_factory, settings_factory
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

slack_settings = settings_factory().get("apps").get("slack")

rulesdata = [

    """
    Notify onboarded (READY)
    """,
    {
        rulename: "on-device-ready-notify",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadMatchOne("$.value", "READY"),
            ],
            processing: [
                PyCall(
                    requests.post,
                    args=(slack_settings["devices_channel_url"],),
                    kawrgs=lambda subject: {
                        "json": {
                            "type": "mrkdwn",
                            "text": ":+1: device *{}* on board! ".format(subject.name)
                        }
                    }
                ),

            ],
        },
    },

    """
    Notify ACTIVE
    """,
    {
        rulename: "on-device-active-notify",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadMatchOne("$.value",  "ACTIVE"),
            ],
            processing: [
                PyCall(
                    requests.post,
                    args=(slack_settings["devices_channel_url"],),
                    kwargs=lambda self: {
                        "json": {
                            "type": "mrkdwn",
                            "text": ":white_check_mark: device *{}* is now *{}*".format(
                                self.subject.name, self.payload.get("value")
                            )
                        }
                    }
                ),

            ],
        },
    },

    """
    Notify INACTIVE
    """,
    {
        rulename: "on-device-inactive-notify",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadMatchOne("$.value",  "INACTIVE"),
            ],
            processing: [
                PyCall(
                    requests.post,
                    args=(slack_settings["devices_channel_url"],),
                    kwargs=lambda self: {
                        "json": {
                            "text": ":ballot_box_with_check: device *{}* become *{}*".format(
                                self.subject.name, self.payload.get("value")
                            )
                        }
                    }
                ),
            ],
        },
    },

]