from datetime import datetime, timedelta

from krules_core.base_functions import *

from krules_core import RuleConst as Const

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

from krules_core.providers import results_rx_factory, subject_factory, message_router_factory
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


class IsEnabled(RuleFunctionBase):

    def execute(self):

        return getattr(self.subject, "m_isEnabled", False)


class Schedule(RuleFunctionBase):

    def execute(self, message=None, subject=None, payload=None, when=lambda _: datetime.now(), replace=False):

        if message is None:
            message = self.message
        if subject is None:
            subject = self.subject
        if payload is None:
            payload = self.payload

        if str(self.subject) != str(subject):
            subject = subject_factory(str(subject), event_info=self.subject.event_info())

        if callable(when):
            when = when(self)
        if type(when) is not str:
            when = when.isoformat()

        new_payload = {"message": message, "subject": str(subject), "payload": payload, "when": when, "replace": replace}

        message_router_factory().route("schedule-message", subject, new_payload,
                                       dispatch_policy=DispatchPolicyConst.DIRECT)


rulesdata = [

    """
    When data received set device status 'ACTIVE',
    then, schedule the message to set it 'INACTIVE'
    Each time some data is received, the change of state to inactive is delayed
    """,
    {
        rulename: "on-data-received-set-status-active",
        subscribe_to: "data-received",
        ruledata: {
            filters: [
                IsEnabled(),
            ],
            processing: [
                SetSubjectProperty("status", 'ACTIVE'),
                Schedule("set-device-status", payload={'value': 'INACTIVE'},
                         when=lambda subject: datetime.now()+timedelta(seconds=int(subject.rate)), replace=True)
            ],
        },
    },

    """
    Set device status, used to set INACTIVE by the scheduler
    """,
    {
        rulename: 'on-set-device-status',
        subscribe_to: "set-device-status",
        ruledata: {
            processing: [
                SetSubjectProperty("status", lambda payload: payload["value"])
            ]
        }
    },

]