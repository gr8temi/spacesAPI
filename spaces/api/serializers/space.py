from rest_framework import serializers
from ..models.spaces import Space


class SpaceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format="hex")
    class Meta:
        model = Space
        fields = ('id', 'number_of_bookings', 'agent', 'description', 'price', 'created_at',
                  'space_category', 'location', 'name', 'availabilty', 'objects', 'updated_at')
