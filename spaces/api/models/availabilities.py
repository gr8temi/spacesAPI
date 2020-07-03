import uuid
from django.db import models
from .spaces import Space

          
class Availability(models.Model):
    availability_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    day = models.CharField(max_length=50)
    all_day = models.BooleanField()
    open_time  = models.TimeField(null = True, auto_now=False, auto_now_add=False)
    close_time = models.TimeField(null = True, auto_now=False, auto_now_add=False)
    
    def __str__(self):
        return self.space