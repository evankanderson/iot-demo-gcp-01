from datetime import datetime

from krules_core.base_functions import *

from krules_core import RuleConst as Const

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING


from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

from dateutil.parser import parse

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


class IsNotOutdated(RuleFunctionBase):

    def execute(self, key_func):

        key = key_func(self)
        event_time = parse(self.payload["_event_info"]["Time"])
        last_received = getattr(self.subject, key, None)
        if last_received is None:
            setattr(self.subject, key, event_time.isoformat())
            return True
        if parse(last_received) > event_time:
            return False
        setattr(self.subject, key, event_time.isoformat())
        return True


rulesdata = [

    """
    Just emit "data-received" event
    Data should be handled by application specific logic
    """,
    {
        rulename: "on-data-received-propagate",
        subscribe_to: "google.pubsub.topic.publish",
        ruledata: {
            filters: [
                IsNotOutdated(lambda payload: "data-received#{}".format(payload.get("deviceid")))
            ],
            processing: [
                SetSubjectPropertySilently("m_lastSeen", datetime.now().isoformat()),
                Route("data-received",                                  # message
                      lambda payload: payload.pop("deviceid"),          # subject
                      lambda payload: {                                 # payload
                          "receivedAt": payload["_event_info"]["Time"],
                          "data": payload
                      }),
            ],
        },
    },

]