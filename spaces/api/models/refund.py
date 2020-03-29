import uuid
from django.db import models
from .user import User
from .order import Order
from .spaces import Space


class Refund(models.Model):
    refund_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return self.order
    