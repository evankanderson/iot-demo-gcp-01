from krules_core.base_functions import *

from krules_core import RuleConst as Const, TopicsDefault
from krules_core.base_functions.misc import PyCall

import requests
import os

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
    Give the chance to subscribe specific error conditions from the source originating the error
    """,
    {
        rulename: "on-errors-propagate",
        subscribe_to: TopicsDefault.RESULTS,
        ruledata: {
            filters: [
                IsTrue(lambda payload: payload["got_errors"])
            ],
            processing: [
                Route(
                    lambda payload: "{}-errors".format(payload["_event_info"]["Source"]),
                    lambda payload: payload["subject"],
                    lambda payload: payload
                )
            ],
        },
    },

    """
    Notify on mattermost
    """,
    {
        rulename: 'on-errors-notify',
        subscribe_to: TopicsDefault.RESULTS,
        ruledata: {
            filters: [
                IsTrue(lambda payload: payload["got_errors"])
            ],
            processing: [
                PyCall(
                    requests.post,
                    os.environ["SLACK_CHANNEL_URL"],
                    json=lambda jp_match1, payload: {
                        "text": ":ambulance: *{}[{}]* \n```\n{}\n```".format(
                            payload["_event_info"]["Source"],
                            payload["rule_name"],
                            "\n".join(jp_match1("$.processing[*].exc_info", payload))
                        )
                    }
                ),
            ]
        }
    },
]