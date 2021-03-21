from import_export import resources
from api.models.extras import Extra

class ExtraResource(resources.ModelResource):
    class Meta:
        model = Extra
