from rest_framework import serializers
from ..models.extras import Extra


class ExtraSerializer(serializers.ModelSerializer):

    class Meta:
        model = Extra
        fields = ["space", "name", "cost"]