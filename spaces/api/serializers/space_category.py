from rest_framework import serializers
from ..models.spaces_category import SpaceCategory


class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceCategory
        fields = "__all__"