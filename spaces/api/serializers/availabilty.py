from ..models.availabilities import Availability
from rest_framework import serializers


class AvailabilitySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Availability
        fields = ["space", "day", "all_day", "open_time", "close_time"]

    @property
    def custom_full_errors(self):
        """
        Returns full errors formatted as per requirements
        """
        default_errors = self.errors # default errors dict
        error_messages = []
        for field_name, field_errors in default_errors.items():
            for field_error in field_errors:
                error_message = '%s: %s'%(field_name, field_error)
                error_messages.append(error_message) 
        error_messages_string = ' '.join(error_messages)
        return error_messages_string
