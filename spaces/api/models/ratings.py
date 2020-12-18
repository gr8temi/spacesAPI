import uuid
from django.db import models
from .user import User
from .spaces import Space

class Rating(models.Model):
    rating_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ratings = models.FloatField()
    comment = models.TextField()
    user = models.CharField(max_length=250, default=" ")
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    def __str__(self):
        return self.space
    