from django.apps import apps
from django.contrib import admin
from .models.spaces import Space
from django.utils.html import format_html
from import_export.formats import base_formats
from import_export.admin import ExportMixin
from .resources.spaces_resource import SpaceResource

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

    def change_active(self, id):
        space_obj = Space.objects.get(space_id=id)
        space_obj.active = not space_obj.active
        space_obj.save()

        # if space_obj.active:
        #     space_obj.active = False
        #     space_obj.save()
        # else:
        #     space_obj.active = True
        #     space_obj.save()

    def freeze_btn(self, obj):
        if obj.active:
            return format_html('<button type="submit" style="background:#66c2ff; width:70px; height:25px; '
                               'border-radius:25px; outline:none; border:none; cursor:pointer; color:white;" '
                               'href="#" onclick="{}">Freeze</button>'.format(SpaceAdmin.change_active(self, obj.space_id)))

        return format_html('<button type="submit" style="background:#66c2ff; width:70px; height:25px; '
                           'border-radius:25px; outline:none; border:none; cursor:pointer; color:white;"'
                           'href="#" onclick="{}" >Unfreeze</button>'.format(SpaceAdmin.change_active(self, obj.space_id)))

    freeze_btn.short_description = 'action'


for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
