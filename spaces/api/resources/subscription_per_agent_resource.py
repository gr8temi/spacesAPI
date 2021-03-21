from import_export import resources
from api.models.subscription import SubscriptionPerAgent

class SubscritptionPerAgentResource(resources.ModelResource):
    class Meta:
        model = SubscriptionPerAgent
