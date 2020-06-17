from rest_framework import serializers
from ..models.order import Order
from ..models.order_extras import OrderExtra


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        