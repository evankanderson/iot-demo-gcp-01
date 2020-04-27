import requests

from krules_core.base_functions import *

from krules_core import RuleConst as Const
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
results_rx_factory().subscribe(
    on_next=publish_results_all,
)
# results_rx_factory().subscribe(
#     on_next=publish_results_errors,
# )

slack_settings = settings_factory().get("apps").get("slack").get("web_hooks")


rulesdata = [

    """
    On status NORMAL notify
    """,
    {
        rulename: "on-temp-status-back-to-normal-websocket-notifier",
        subscribe_to: "temp-status-back-to-normal",
        ruledata: {
            processing: [
                PyCall(
                    requests.post,
                    slack_settings["device_status_change_url"],
                    json=lambda subject: {
                        "text": " :sunglasses:  device *{}* temp status back to normal! ".format(subject.name)
                    }
                ),
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
                PyCall(
                    requests.post,
                    slack_settings["device_status_change_url"],
                    json=lambda self: {
                        "text": ":scream:  device *{}* is *{}* ({}°C)".format(
                            self.subject.name, self.payload.get("status"), self.payload.get("tempc")
                        )
                    }
                ),
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
                PyCall(
                    requests.post,
                    slack_settings["device_status_change_url"],
                    json=lambda self: {
                        "text": ":neutral_face: device *{}* is still *{}* from {} secs".format(
                            self.subject.name,
                            self.payload.get("status"),
                            self.payload.get("seconds")
                        )
                    }
                ),
            ],
        },
    },

]
