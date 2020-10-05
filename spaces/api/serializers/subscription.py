from rest_framework import serializers
from ..models.subscription import Subscription, SubscriptionPerAgent, BillingHistory


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = "__all__"


class SubPerAgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionPerAgent
        fields = "__all__"


class BillHistSerializer(serializers.ModelSerializer):

    class Meta:
        model = BillingHistory
        fields = "__all__"
