from rest_framework import serializers
from ..models.customer import Customer
from api.serializers.user import UserSerializer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        # depth = 1


class CustomerSerializerDetail(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Customer
        fields = ['customer_id', 'user']
        depth = 1
