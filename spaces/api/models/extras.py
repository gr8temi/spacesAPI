import uuid
from django.db import models
from .spaces import Space


class Extra(models.Model):
    extra_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey("api.Space", on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    cost = models.IntegerField(default=0)
    duration = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.space}"
    
