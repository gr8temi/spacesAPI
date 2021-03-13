import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class SpaceCategory(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space_category = models.CharField( max_length=50)
    images = ArrayField(base_field=models.CharField(max_length=256, ),blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)

    class Meta:
        verbose_name_plural = 'Space categories'

    def __str__(self):
        return self.space_category

    def category(self):
        return self.space_category

    def image(self):
        return self.images[0]  #if no image is uploaded, it would cause an error
