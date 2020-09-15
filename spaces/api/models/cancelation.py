import uuid
from django.db import models
from .customer import Customer
from .agent import Agent
from .order import Order

class Cancellation(models.Model):
    cancellation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    reason = models.TextField()
    booking = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=10,default="pending")

    def __str__(self):
        return self.cancellation_id