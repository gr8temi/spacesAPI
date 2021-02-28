from rest_framework.serializers import ModelSerializer
from ..models.cancellation_rules import CancellationRules

class CancellationRulesSerializer(ModelSerializer):

    class Meta:
        model = CancellationRules
        fields = "__all__"