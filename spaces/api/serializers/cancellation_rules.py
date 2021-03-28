from rest_framework.serializers import ModelSerializer
from ..models.cancellation_rules import CancellationRules

class CancellationRulesSerializer(ModelSerializer):

    class Meta:
        model = CancellationRules
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
