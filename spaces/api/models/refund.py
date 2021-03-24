import uuid
from django.db import models
from .user import User
from .order import Order
from .spaces import Space


class Refund(models.Model):
    refund_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name= 'Space Host', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.order)

    def space_host(self):
        return self.order.agent_name()

    def space_host_business_name(self):
        return self.space.space_host_business_name()

    def customer(self):
        return self.user

    def order_name(self):
        return self.order.name

    def order_code(self):
        return self.order
