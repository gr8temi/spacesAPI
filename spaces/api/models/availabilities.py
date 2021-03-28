import uuid
from django.db import models

          
class Availability(models.Model):
    availability_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey("api.Space", on_delete=models.CASCADE, null=True)
    day = models.CharField(max_length=50)
    all_day = models.BooleanField()
    open_time  = models.TimeField(null = True, auto_now=False, auto_now_add=False)
    close_time = models.TimeField(null = True, auto_now=False, auto_now_add=False)

    class Meta:
        verbose_name_plural = "Availabilities"
    
    def __str__(self):
        return self.space.name

    def space_host(self):
        return self.space.agent.user

    def space_host_business_name(self):
        return self.space.agent
