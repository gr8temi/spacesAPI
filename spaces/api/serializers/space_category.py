from rest_framework import serializers
from ..models.spaces_category import SpaceCategory


class SpaceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format="hex")
    print(id)
    class Meta:
        model = SpaceCategory
        fields = "__all__"