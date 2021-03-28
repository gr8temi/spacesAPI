import uuid
from django.db import models
from .user import User

class Customer(models.Model):
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def phone_number(self):
        return self.user.phone_number

    def email_address(self):
        return self.user.email
        
    def __str__(self):
        return self.user.name
    