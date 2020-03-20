import uuid
from django.db import models
from .space import Space


class Amenities(models.Model):
    name = models.CharField(max_length=50)
    amount = models.IntegerField()
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    condition = models.BooleanField(default=True)
    created_at = models.DateTimeField( auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)

    def __str__(self):
        return self.name
    