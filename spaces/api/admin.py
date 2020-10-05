from django.apps import apps
from django.contrib import admin
# from api.models.availabilities import Availability
models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
# admin.site.register(Availability)
