import uuid
from django.db import models
from .customer import Customer
from .agent import Agent
from .order import Order


STATUS_CHOICES = [
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("rejected", "Rejected")
]

class Cancellation(models.Model):
    cancellation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    reason = models.TextField()
    booking = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.cancellation_id}"

    def cancellation_policy(self):
        return self.booking.space.cancellation_rules
