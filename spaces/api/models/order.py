import uuid
from django.db import models
from .user import User
from .order_type import OrderType
from .spaces import Space
from .cancellation_rules import CancellationRules
from django.contrib.postgres.fields.jsonb import JSONField as JSONBField
from django.contrib.postgres.fields import ArrayField, JSONField
# from jsonfield import JSONField

from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone


class Order(models.Model):
    orders_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.CharField(max_length=50, default=0)
    name = models.CharField(max_length=50, default="new")
    company_email = models.CharField(max_length=100, default="one@gmail.com")
    no_of_guest = models.IntegerField()
    extras = JSONBField(null=True, blank=True, default=dict,
                        encoder=DjangoJSONEncoder)
    usage_start_date = models.DateTimeField(null=True, blank=True)
    usage_end_date = models.DateTimeField(null=True, blank=True)
    hours_booked = JSONBField(null=True, blank=True,
                              default=dict, encoder=DjangoJSONEncoder)
    days_booked = JSONBField(null=True, blank=True,
                             default=dict, encoder=DjangoJSONEncoder)
    status = models.CharField(max_length=30)
    transaction_code = models.CharField(max_length=300, null=True, blank=True)
    order_code = models.CharField(max_length=30)
    order_type = models.ForeignKey(OrderType, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name="order")
    order_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    cancellation_policy = models.ForeignKey(CancellationRules, null=True, on_delete=models.CASCADE)

    def space_name(self):
        return self.space.name

    def space_description(self):
        return self.space.description

    def agent_name(self):
        return self.space.agent.user.name

    def agent_id(self):
        return self.space.agent.agent_id

    def duration(self):
        return self.space.duration

    def images(self):
        return self.space.images

    def user_id(self):
        return self.user.user_id
        
    def space_address(self):
        return self.space.address

    def __str__(self):
        return self.order_code
