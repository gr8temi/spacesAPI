from import_export import resources
from api.models.subscription import BillingHistory


class BillingHistoryResource(resources.ModelResource):
    class Meta:
        model = BillingHistory
