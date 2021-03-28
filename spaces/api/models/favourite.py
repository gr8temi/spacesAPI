import uuid
from django.db import models
from .spaces import Space
from .user import User

class Favourite(models.Model):

    favorite_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    space = models.OneToOneField(Space, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.space} {self.user}"
    