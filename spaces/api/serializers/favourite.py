from rest_framework import serializers
from ..models.favourite import Favourite
from ..serializers.space import SpaceSerializer

class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = "__all__"

class FavouriteSpaceSerializer(serializers.ModelSerializer):
    space = SpaceSerializer(read_only=True)

    class Meta:
        model = Favourite
        fields = "__all__"
