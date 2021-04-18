import uuid
from django.db import models
from .space_type import SpaceType
from .agent import Agent
from .cancellation_rules import CancellationRules
from django.contrib.postgres.fields import ArrayField, JSONField
import json
from django.core.serializers.json import DjangoJSONEncoder


class SpaceManager(models.Manager):
    def get_spaces_by_availability(self, available):
        spaces = self.objects.filter(availability=available)
        count = spaces.count()
        return {"spaces": spaces, "count": count}


class Space(models.Model):
    space_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField()
    space_type = models.ForeignKey(SpaceType, on_delete=models.CASCADE, null=True)
    address = JSONField(encoder=DjangoJSONEncoder)
    city = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    gmap = JSONField(encoder=DjangoJSONEncoder)
    number_of_bookings = models.IntegerField(null=True, blank=True, default=0)
    capacity = models.IntegerField()
    amount = models.IntegerField(default=0)
    agent = models.ForeignKey(Agent, verbose_name="Space Host Business Name", on_delete=models.CASCADE)
    duration = models.CharField(max_length=50)
    images = ArrayField(base_field=models.CharField(max_length=256))
    amenities = ArrayField(base_field=models.CharField(max_length=50))
    carspace = models.IntegerField(default=0)
    rules = ArrayField(base_field=models.CharField(max_length=50))
    cancellation_rule = models.ForeignKey(
        CancellationRules,
        on_delete=models.CASCADE,
        null=True,
    )
    objects = SpaceManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    ratings = models.FloatField(default=0)
    image_details = JSONField(default=dict(image="image"), encoder=DjangoJSONEncoder)

    def space_type_name(self):
        return self.space_type

    def space_host(self):
        return self.agent.user
    
    def space_host_business_name(self):
        return self.agent

    def category_name(self):
        return self.space_type.space_category

    def __str__(self):
        return self.name
