from rest_framework import serializers
from ..models.cancelation import Cancellation


class CancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancellation
        fields = "__all__"


class CancellationFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancellation
        fields = "__all__"
        depth = 2
