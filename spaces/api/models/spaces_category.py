import uuid
from django.db import models


class SpaceCategory(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space_category = models.CharField( max_length=50)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)

    def __str__(self):
        return self.space_category