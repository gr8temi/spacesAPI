from ..models.availabilities import Availability
from rest_framework import serializers


class AvailabilitySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Availability
        fields = ["space", "day", "all_day", "open_time", "close_time"]