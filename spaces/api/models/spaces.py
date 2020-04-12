import uuid
from django.db import models
from .spaces_category import SpaceCategory
from .agent import Agent
from django.contrib.postgres.fields import ArrayField

class SpaceManager(models.Manager):
    def get_spaces_by_availability(self,available):
        spaces = self.objects.filter(availability=available)
        count = spaces.count()
        return {"spaces":spaces,"count":count}
        
class Space(models.Model):
    space_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number_of_bookings = models.IntegerField(null=True,blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    description = models.TextField()
    price  = models.CharField( max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    space_category = models.ForeignKey(SpaceCategory, on_delete=models.DO_NOTHING)
    location  = models.TextField()
    name  = models.CharField(max_length=50)
    images = ArrayField(base_field=models.CharField(max_length=256))
    facilities = ArrayField(base_field=models.CharField(max_length=50))
    rules = ArrayField(base_field=models.CharField(max_length=50))
    videos = ArrayField(base_field=models.CharField(max_length=256))
    objects = SpaceManager()
    updated_at = models.DateTimeField( auto_now=True)
    
    def __str__(self):
        return self.name

