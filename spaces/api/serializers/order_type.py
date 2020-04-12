from rest_framework import serializers
from ..models.order_type import OrderType


class OrderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderType
        fields = "__all__"
