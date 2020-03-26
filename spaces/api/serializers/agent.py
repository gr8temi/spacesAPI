from rest_framework import serializers
from ..models.agent import Agent


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = "__all__"