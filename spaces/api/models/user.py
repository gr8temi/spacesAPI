import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder


class UserManager(models.Manager):
    def user_count(self):
        return self.objects.all().count()

    def user_active(self):
        return self.objects.filter(is_active=True)

    def user_active_count(self):
        return self.objects.filter(is_active=True).count()


class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, default="John doe")
    email = models.EmailField(max_length=254, unique=True)
    phone_number = models.CharField(max_length=14, unique=True)
    password = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)
    is_super = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    token = models.CharField(max_length=20)
    objects = UserManager()
    updated_at = models.DateTimeField( auto_now=True)
    date_of_birth = models.DateField( null=True )
    social_links = JSONField(encoder=DjangoJSONEncoder, null=True)
    profile_url = models.CharField(max_length=256, blank=True)
    def __str__(self):
        return self.name
