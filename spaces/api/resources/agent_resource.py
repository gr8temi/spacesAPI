from import_export import resources
from api.models.agent import Agent


class AgentResource(resources.ModelResource):
    class Meta:
        model = Agent
