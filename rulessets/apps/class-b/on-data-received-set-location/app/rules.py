from krules_core.base_functions import *

from krules_core import RuleConst as Const

from geopy import distance
from geopy.geocoders import Nominatim


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

geolocator = Nominatim(user_agent="KRules", timeout=10)


class SetLocationProperties(RuleFunctionBase):

    def execute(self):

        coords = (float(self.payload["data"]["lat"]), float(self.payload["data"]["lng"]))
        self.subject.coords = str(coords)
        # ensure ref point is already set
        if "m_refCoords" not in self.subject:
            self.subject.m_refCoords = str(coords)
        # set location if not already set or if tolerance is exceeded
        if "location" not in self.subject or distance.distance(
                self.subject.m_refCoords, coords
            ).meters > float(self.subject.tolerance):
            self.subject.location = geolocator.reverse("{}, {}".format(coords[0], coords[1])).address
            self.subject.m_refCoords = coords


rulesdata = [

    """
    Always store coords in subject, Initialize starting point too if needed
    """,
    {
        rulename: "on-data-received-store-coords",
        subscribe_to: "data-received",
        ruledata: {
            processing: [
                SetLocationProperties()
            ],
        },
    },

]
