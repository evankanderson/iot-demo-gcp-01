import os

import requests

from app_functions import SlackPublishMessage
from krules_core.base_functions import *

from krules_core import RuleConst as Const, messages
from krules_core.base_functions.misc import PyCall

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
        rulename: "on-device-ready-notify",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                IsTrue(lambda payload: payload.get("value") == "READY"),
            ],
            processing: [
                SlackPublishMessage(
                    channel="devices_channel",
                    text=lambda subject: ":+1: device *{}* on board! ".format(subject.name)
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
                IsTrue(lambda payload: payload.get("value") == "ACTIVE"),
            ],
            processing: [
                SlackPublishMessage(
                    channel="devices_channel",
                    text=lambda self: ":white_check_mark: device *{}* is now *{}*".format(
                                self.subject.name, self.payload.get("value")
                            )
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
                IsTrue(lambda payload: payload.get("value") == "INACTIVE"),
            ],
            processing: [
                SlackPublishMessage(
                    channel="devices_channel",
                    text=lambda self: ":ballot_box_with_check: device *{}* become *{}*".format(
                                self.subject.name, self.payload.get("value")
                            )
                ),
            ],
        },
    },

]