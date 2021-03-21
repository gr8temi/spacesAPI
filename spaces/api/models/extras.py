import uuid
from django.db import models
from .spaces import Space


class Extra(models.Model):
    extra_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey("api.Space", on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    cost = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.space}"

    def extra(self):
        return self.name

    def space_name(self):
        return self.space.name

    def space_address(self):
        return self.space.address

    def space_capacity(self):
        return self.space.capacity

    def space_amount(self):
        return self.space.amount

    def agent(self):
        return self.space.agent.user.name

    def extra_cost(self):
        return self.cost
