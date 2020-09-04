import uuid
from django.db import models


class Notification(models.Model):

    notification_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False)
    notification = models.TextField()
    user_id = models.UUIDField(null=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
