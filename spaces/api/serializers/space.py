from rest_framework import serializers
from ..models.spaces import Space


class SpaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Space
        fields = ['name', 'description', 'space_category', 'address', 'gmap', 'number_of_bookings', 'capacity', 'amount', 'agent', 'duration', 'images', 'videos', 'amenities', 'carspace', 'rules', 'cancellation_rules']
