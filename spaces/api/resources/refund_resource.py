from import_export import resources
from api.models.refund import Refund

class RefundResource(resources.ModelResource):
    class Meta:
        model = Refund
