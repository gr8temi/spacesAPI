from import_export import resources
from api.models.cancellation_rules import CancellationRules


class CancellationRulesResource(resources.ModelResource):
    class Meta:
        model = CancellationRules
        excludes = ('description')
