from import_export import resources
from api.models.subscription import SubscriptionPerAgent

class SubscriptionPerAgentResource(resources.ModelResource):
    class Meta:
        model = SubscriptionPerAgent
