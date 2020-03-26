from rest_framework import serializers
from ..models.spaces import Space


class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = "__all__"
