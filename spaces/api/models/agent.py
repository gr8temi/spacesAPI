import uuid
from django.db import models
from .user import User

PLANS = [
    ("subscription", "Subscription"),
    ("commission", "Commission"),
]

class Agent(models.Model):
    agent_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, verbose_name='Space Host', on_delete=models.CASCADE)
    business_name = models.CharField(max_length=50)
    office_address = models.CharField(max_length=50)
    account_number = models.CharField(max_length=10, blank=True)
    account_name = models.CharField(max_length=50, blank=True)
    bank = models.CharField(max_length=256, blank=True)
    document = models.CharField(max_length=256, blank=True)
    plans = models.CharField(choices=PLANS, max_length=50, default="commission")
    validated = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'space host'
        verbose_name_plural = 'Space hosts'
        
    def __str__(self):
        return self.business_name
