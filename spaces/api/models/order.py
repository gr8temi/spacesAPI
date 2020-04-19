import uuid
from django.db import models
from .user import User
from .order_type import OrderType
from .spaces import Space

class Order(models.Model):
    orders_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usage_start_date = models.DateField()
    usage_end_date = models.DateField()
    status = models.CharField(max_length=30)
    transaction_code = models.CharField(max_length=30)
    order_code = models.CharField(max_length=30)
    order_type = models.ForeignKey(OrderType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return self.order_code
