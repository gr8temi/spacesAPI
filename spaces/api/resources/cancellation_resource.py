from import_export import resources
from api.models.cancelation import Cancellation

class CancellationResource(resources.ModelResource):
    class Meta:
        model = Cancellation
