from rest_framework import serializers
from ..models.customer import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        # depth = 1


class CustomerSerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        depth = 1
