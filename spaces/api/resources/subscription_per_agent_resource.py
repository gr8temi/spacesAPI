from import_export import resources
from api.models.subscription import SubscriptionPerAgent

class SubscriptionPerSpaceHostResource(resources.ModelResource):
    class Meta:
        model = SubscriptionPerAgent
