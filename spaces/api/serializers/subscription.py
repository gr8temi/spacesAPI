from rest_framework import serializers
from ..models.subscription import Subscription, SubscriptionPerAgent, BillingHistory


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"

    @property
    def custom_full_errors(self):
        """
        Returns full errors formatted as per requirements
        """
        default_errors = self.errors  # default errors dict
        error_messages = []
        for field_name, field_errors in default_errors.items():
            for field_error in field_errors:
                error_message = "%s: %s" % (field_name, field_error)
                error_messages.append(error_message)
        error_messages_string = " ".join(error_messages)
        return error_messages_string


class SubPerAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPerAgent
        fields = [
            "sub_per_agent_id",
            "subscription_name",
            "subscription_type",
            "subscription_plan",
            "space_host",
            "subscription",
            "recurring",
            "next_due_date",
            "paid",
            "paid_at",
            "is_cancelled",
            "reference_code",
            "agent",
            "amount",
        ]

    @property
    def custom_full_errors(self):
        """
        Returns full errors formatted as per requirements
        """
        default_errors = self.errors  # default errors dict
        error_messages = []
        for field_name, field_errors in default_errors.items():
            for field_error in field_errors:
                error_message = "%s: %s" % (field_name, field_error)
                error_messages.append(error_message)
        error_messages_string = " ".join(error_messages)
        return error_messages_string


class BillHistSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingHistory
        fields = "__all__"

    @property
    def custom_full_errors(self):
        """
        Returns full errors formatted as per requirements
        """
        default_errors = self.errors  # default errors dict
        error_messages = []
        for field_name, field_errors in default_errors.items():
            for field_error in field_errors:
                error_message = "%s: %s" % (field_name, field_error)
                error_messages.append(error_message)
        error_messages_string = " ".join(error_messages)
        return error_messages_string
