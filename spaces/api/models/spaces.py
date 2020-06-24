import uuid
from django.db import models
from .spaces_category import SpaceCategory
from .agent import Agent
from django.contrib.postgres.fields import ArrayField, JSONField
import json
from django.core.serializers.json import DjangoJSONEncoder


class SpaceManager(models.Manager):
    def get_spaces_by_availability(self, available):
        spaces = self.objects.filter(availability=available)
        count = spaces.count()
        return {"spaces": spaces, "count": count}


class Space(models.Model):
    space_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField()
    space_category = models.ForeignKey(
        SpaceCategory, on_delete=models.DO_NOTHING)
    address = JSONField(encoder=DjangoJSONEncoder)
    gmap = JSONField(encoder=DjangoJSONEncoder)
    number_of_bookings = models.IntegerField(null=True, blank=True, default=0)
    capacity = models.IntegerField()
    amount = models.IntegerField(default=0)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    duration = models.CharField(max_length=50)
    images = ArrayField(base_field=models.CharField(max_length=256))
    # videos = ArrayField(base_field=models.CharField(max_length=256))
    amenities = ArrayField(base_field=models.CharField(max_length=50))
    carspace = models.IntegerField(default=0)
    rules = ArrayField(base_field=models.CharField(max_length=50))
    cancellation_rules = ArrayField(
        base_field=models.CharField(max_length=256))
    objects = SpaceManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
