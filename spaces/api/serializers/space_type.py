from rest_framework import serializers
from ..models.space_type import SpaceType


class SpaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceType
        fields = "__all__"


class SpaceTypeSerializerDetails(serializers.ModelSerializer):
    class Meta:
        model = SpaceType
        fields = "__all__"
        depth = 1
