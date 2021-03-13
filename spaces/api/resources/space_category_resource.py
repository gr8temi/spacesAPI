from import_export import resources
from api.models.spaces_category import SpaceCategory

class SpaceCategoryResource(resources.ModelResource):
    class Meta:
        model = SpaceCategory
