from krules_core.base_functions import *

from krules_core import RuleConst as Const

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

from krules_core.providers import results_rx_factory, subject_factory, message_router_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

from cloudstorage.drivers.google import GoogleStorageDriver
from krules_cloudstorage.csv import ProcessCSV_AsDict

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

rulesdata = [

    """
    My wonderful rule description
    """,
    {
        rulename: "on-csv-upload-import-devices",
        subscribe_to: "google.storage.object.finalize",
        ruledata: {
            filters: [
                CheckSubjectMatch("onboarding/import/(?P<deviceclass>.+)/(?P<filename>.+)", payload_dest="path_info"),
                CheckPayloadMatchOne("$.contentType", "text/csv")
            ],
            processing: [
                ProcessCSV_AsDict(
                    driver=GoogleStorageDriver,
                    bucket=lambda payload: payload["bucket"],
                    path=lambda payload: payload["name"],
                    func=lambda device_data, self: (
                        message_router_factory().route(
                            "onboard-device",
                            subject_factory(device_data.pop("deviceid"), event_info=self.subject.event_info()),
                            {
                                "data": device_data,
                                "class": self.payload["path_info"]["deviceclass"]
                            }),
                    )
                )
            ],
        },
    },

]