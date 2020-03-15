import uuid
from django.db import models


class OrderType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_type = models.CharField( max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_type
    