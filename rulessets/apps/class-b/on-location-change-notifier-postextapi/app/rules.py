import hashlib
import os
from datetime import datetime, timedelta

import pytz

from app_functions import Schedule
from krules_core.base_functions import *

from krules_core import RuleConst as Const, messages

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING
import jsonpath_rw_ext as jp

from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered
import requests

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


class PostExtApi(RuleFunctionBase):

    def execute(self, url, req_kwargs, on_response):
        resp = requests.post(url, **req_kwargs)
        self.payload["response_status"] = resp.status_code
        self.payload["response_text"] = resp.text
        on_response(self, resp)


rulesdata = [

    """
    Dispose api call
    """,
    {
        rulename: "on-location-changed-notify-postextapi",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("location"),
            ],
            processing: [
                Route("do-extapi-post", payload=lambda self: {
                    "url": os.environ["EXTAPI_URL"],
                    # https://europe-west3-krules-dev-254113.cloudfunctions.net/store_devices_location
                    "req_kwargs": {
                        "headers": {},  # {"x-api-key": os.environ["EXTAPI_X_API_KEY"]},
                        "json": {
                            "device": self.subject.name,
                            "timestamp": datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat(),
                            "coords": self.subject.get("coords"),
                            "location": self.payload["value"],
                        }
                    },
                }, dispatch_policy=DispatchPolicyConst.NEVER)
            ],
        },
    },

    """
    Do call api
    """,
    {
        rulename: "on-do-extapi-post",
        subscribe_to: "do-extapi-post",
        ruledata: {
            processing: [
                PostExtApi(
                    url=lambda payload: payload["url"],
                    req_kwargs=lambda payload: payload["req_kwargs"],
                    on_response=lambda self, resp: (
                        resp.raise_for_status(),
                        resp.status_code == 503 and resp.raise_for_status()
                        ## do something when success...,
                        # eg: Route("on-extapi-post.success", payload=resp.json())
                    )
                )
            ]
        }
    },

    """
    Manage exception
    """,
    {
        rulename: "on-do-extapi-post-errors",
        subscribe_to: "{}-errors".format(os.environ["K_SERVICE"]),
        ruledata: {
            filters: [
                IsTrue(lambda payload:
                       payload.get("rule_name") == "on-do-extapi-post" and
                       jp.match1("$.processing[*].exception", payload) == "requests.exceptions.HTTPError" and
                       jp.match1("$.processing[*].exc_extra_info.response_code", payload) == 503)
            ],
            processing: [
                Schedule(
                    message="do-extapi-post",
                    schedule_hash=lambda payload: hashlib.md5(
                        "{}{}".format(payload["payload"]["req_kwargs"]["json"]["device"],
                                      payload["payload"]["req_kwargs"]["json"]["timestamp"]
                                      ).encode('utf-8')).hexdigest(),
                    payload=lambda payload: payload["payload"],
                    when=lambda _: (datetime.now() + timedelta(seconds=10)).isoformat(), replace=True),
            ]
        }
    }

]
