from import_export import resources
from api.models.subscription import Subscription

class SubscriptionResource(resources.ModelResource):
    class Meta:
        model = Subscription
