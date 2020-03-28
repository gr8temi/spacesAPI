import uuid
from django.db import models
from .user import User


class Agent(models.Model):
    agent_id =  models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField( max_length=50)
    office_address =models.CharField( max_length=50)
    validated = models.BooleanField(default=False)
    updated_at = models.DateTimeField( auto_now=True)
    created_at = models.DateTimeField( auto_now_add=True)
    
    def __str__(self):
        return self.name
    