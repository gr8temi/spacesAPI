import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from .spaces_category import SpaceCategory


class SpaceType(models.Model):
    space_type_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    space_type  = models.CharField(max_length=50)
    space_category = models.ForeignKey(SpaceCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.space_type
