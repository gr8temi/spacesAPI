import uuid
from django.db import models
from .user import User
from .order_type import OrderType
from .spaces import Space
from django.contrib.postgres.fields.jsonb import JSONField as JSONBField
from django.contrib.postgres.fields import ArrayField, JSONField
# from jsonfield import JSONField

from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone


class Order(models.Model):
    orders_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.CharField(max_length=50, default=0)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company_email = models.CharField(max_length=100, default="one@gmail.com")
    no_of_guest = models.IntegerField()    
    extras = JSONBField(null=True, blank=True, default=dict, encoder=DjangoJSONEncoder)
    usage_start_date = models.DateTimeField(null=True, blank=True)
    usage_end_date = models.DateTimeField(null=True, blank=True)
    hours_booked = JSONBField(null=True, blank=True, default=dict, encoder=DjangoJSONEncoder)
    status = models.CharField(max_length=30)
    transaction_code = models.CharField(max_length=30, null=True)
    order_code = models.CharField(max_length=30)
    order_type = models.ForeignKey(OrderType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank = True, null = True)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return self.order_code
