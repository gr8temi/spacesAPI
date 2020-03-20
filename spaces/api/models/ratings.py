import uuid
from django.db import models
from .user import User
from .space import Space

class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ratings = models.FloatField()
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)

    def __str__(self):
        return self.space
    