from import_export import resources
from api.models.space_type import SpaceType

class SpaceTypeResource(resources.ModelResource):
    class Meta:
        model = SpaceType
