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
from app_functions.cloudstorage.csv import ProcessCSV_AsDict
from app_functions.cloudstorage import DeleteBlob


import pprint
rx = results_rx_factory()
rx.subscribe(
    on_next=pprint.pprint
)
rx.subscribe(
    on_next=publish_results_all,
)
# results_rx_factory().subscribe(
#     on_next=publish_results_errors,
# )

rulesdata = [

    """
    Subscribe to storage, import csv
    """,
    {
        rulename: "on-csv-upload-import-devices",
        subscribe_to: "com.google.cloud.storage.object.finalize",
        ruledata: {
            filters: [
                CheckSubjectMatch("onboarding/import/(?P<deviceclass>.+)/(?P<filename>.+)", payload_dest="path_info"),
                IsTrue(lambda payload: payload.get("contentType") == "text/csv")
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

    {
        rulename: 'on-csv-upload-import-devices-error',
        subscribe_to: "on-gcs-csv-upload-errors",
        ruledata: {
            filters: [
                CheckPayloadMatchOne("$.rule_name", "on-csv-upload-import-devices")
            ],
            processing: [
                # reject file
                DeleteBlob(
                    driver=GoogleStorageDriver,
                    bucket=lambda payload: payload["payload"]["bucket"],
                    path=lambda payload: payload["payload"]["name"]
                )
            ]

        }
    },

]