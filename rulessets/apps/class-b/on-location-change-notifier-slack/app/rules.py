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

slack_settings = settings_factory().get("apps").get("slack").get("web_hooks")

rulesdata = [

    """
    Location changed (changed from a known location)
    """,
    {
        rulename: "on-location-changed-moving-notify-slack",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("location"),
                IsFalse(lambda payload: payload["old_value"] is None)
            ],
            processing: [
                PyCall(
                    requests.post,
                    slack_settings["device_status_change_url"],
                    json=lambda self: {
                        "text": ":rocket: device *{}* moved to {}".format(
                            self.subject.name, self.payload.get("value")
                        )
                    }
                ),
            ]
        }
    },

    """
    Location changed (first location)
    """,
    {
        rulename: "on-location-changed-starting-notify-slack",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("location"),
                IsTrue(lambda payload: payload["old_value"] is None)
            ],
            processing: [
                PyCall(
                    requests.post,
                    slack_settings["device_status_change_url"],
                    json=lambda self: {
                        "text": ":triangular_flag_on_post: device *{}* located in {}".format(
                            self.subject.name, self.payload.get("value")
                        )
                    }
                ),
            ]
        }
    },

]