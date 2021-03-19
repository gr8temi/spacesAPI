from import_export import resources
from api.models.order_type import OrderType

class OrderTypeResource(resources.ModelResource):
    class Meta:
        model = OrderType
