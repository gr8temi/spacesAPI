from import_export import resources
from api.models.availabilities import Availability


class AvailabilityResource(resources.ModelResource):
    class Meta:
        model = Availability
        