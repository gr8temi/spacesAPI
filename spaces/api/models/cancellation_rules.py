import uuid
from django.db import models


class CancellationRules(models.Model):
    cancellation_rule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy = models.CharField(max_length=256)
    description = models.TextField()
    short_description = models.TextField()

    def __str__(self):
        return self.policy