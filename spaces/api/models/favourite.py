import uuid
from django.db import models
from .spaces import Space
from .user import User

class Favourite(models.Model):

    favorite_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, verbose_name='Customer', on_delete=models.CASCADE)
    space = models.OneToOneField(Space, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.space} {self.user}"
    
    def space_name(self):
        return self.space.name

    def user_name(self):
        return self.user.name
    
    def space_type(self):
        return self.space.space_type.space_type
    
    def space_host(self):
        return self.space.agent.user.name

    def space_host_business_name(self):
        return self.space.agent.business_name

