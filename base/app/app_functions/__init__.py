from datetime import datetime

from krules_core.base_functions import RuleFunctionBase, DispatchPolicyConst
from krules_core.providers import subject_factory, message_router_factory


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


class WebsocketNotificationEventClass(object):

    CHEERING = "cheering"
    WARNING = "warning"
    CRITICAL = "critical"
    NORMAL = "normal"
