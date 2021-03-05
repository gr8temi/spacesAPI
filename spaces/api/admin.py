from django.apps import apps
from django.contrib import admin
from .models.spaces import Space
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from import_export.formats import base_formats
from import_export.admin import ExportMixin
from .resources.spaces_resource import SpaceResource
import uuid

# from api.models.availabilities import Availability
models = apps.get_models()


# created this to handle formats types
class ExportMixinAdmin(ExportMixin, admin.ModelAdmin):
    def get_export_formats(self):
        formats = (
            base_formats.CSV,
            base_formats.XLSX,
            base_formats.TSV,
            base_formats.ODS,
            base_formats.JSON,
            base_formats.YAML,
            base_formats.HTML,
        )
        return [f for f in formats if f().can_export()]


class Meta:
    abstract = True


# Spaces display
@admin.register(Space)
class SpaceAdmin(ExportMixinAdmin):
    resource_class = SpaceResource

    list_display = ('space_id', 'name', 'space_type', 'address', 'city', 'state', 'image_tag', 'number_of_bookings',
                    'capacity', 'amount', 'agent', 'duration', 'carspace', 'rules', 'cancellation_rules', 'ratings',
                    'active', 'freeze_btn')
    list_filter = ['agent']
    search_fields = ['agent']

    def image_tag(self, obj):
        return format_html('<img src="{}" style="width: 100px; height: 100px;"/>'.format(obj.images[0]))

    image_tag.short_description = 'Image'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'freeze/<slug:space_id>',
                self.admin_site.admin_view(self.process_freeze),
                name='spaces-freeze',
            ),
            path(
                'unfreeze/<slug:space_id>',
                self.admin_site.admin_view(self.process_unfreeze),
                name='spaces-unfreeze',
            ),
        ]
        return custom_urls + urls

    def freeze_btn(self, obj):
        if obj.active:
            return format_html('<a class="button" href="{}" style="background:#66c2ff; width:75px; '
                               'height:25px; border-radius:25px; outline:none; border:none; cursor:pointer;'
                               'color:white;">Freeze</a>&nbsp;', reverse('admin:spaces-freeze',
                                                                                       args=[str(obj.space_id)]))
        else:
            return format_html('<a class="button" href="{}" style="background:#66c2ff; width:75px; '
                               'height:25px; border-radius:25px; outline:none; border:none; cursor:pointer; '
                               'color:white;">Unfreeze</a>&nbsp;', reverse('admin:spaces-unfreeze',
                                                                                         args=[str(obj.space_id)]))

    def process_freeze(self, request, space_id):
        space_id = uuid.UUID(space_id)
        single_space = Space.objects.get(space_id=space_id)
        single_space.active = False
        single_space.save()
        return redirect('admin:api_space_changelist')

    def process_unfreeze(self, request, space_id):
        space_id = uuid.UUID(space_id)
        single_space = Space.objects.get(space_id=space_id)
        single_space.active = True
        single_space.save()
        return redirect('admin:api_space_changelist')

    freeze_btn.short_description = 'action'


for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
