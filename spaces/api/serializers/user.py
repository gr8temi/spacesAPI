from rest_framework import serializers
from ..models.user import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ["password"]
    
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

class UserRegisterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = "__all__"

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
