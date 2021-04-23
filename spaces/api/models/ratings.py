import uuid
from django.db import models
from .user import User
from .spaces import Space
from .order import Order

class Rating(models.Model):
    rating_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ratings = models.FloatField()
    comment = models.TextField()
    user = models.CharField(verbose_name='Customer', max_length=250, default=None)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.space.name

    def space_name(self):
        return self.space.name

    def space_host(self):
        return self.space.space_host()

    def space_host_business_name(self):
        return self.space.space_host_business_name()

    def space_type(self):
        return self.space.space_type.space_type

    def rating(self):
        return self.ratings
