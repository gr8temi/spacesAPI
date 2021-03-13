import uuid
import csv
from django.apps import apps
from django.http import HttpResponse
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.conf.urls import url
from api.models.cancelation import Cancellation
from api.models.order import Order
from api.resources.cancellation_resource import CancellationResource
from import_export.admin import ExportMixin
from import_export.formats import base_formats
from api.helper.send_cancellation_email import CancellationActions
from django.urls import path, reverse
from django.shortcuts import redirect
from .resources.spaces_resource import SpaceResource
from .models.order import Order
from .models.spaces import Space
from .models.space_type import SpaceType
from .models.spaces_category import SpaceCategory
from .models.agent import Agent
from .models.user import User
from .models.order_type import OrderType
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .resources.order_resource import OrderResource
from .resources.space_type_resource import SpaceTypeResource

# from api.models.availabilities import Availability
models = apps.get_models()

# created this to handle formats types



# created this to handle formats types


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
            return format_html('<a class="button" href="{}" style="background:#66c2ff; display:block; width:75px; '
                               'height:20px; border-radius:5px; outline:none; border:none; cursor:pointer;'
                               'color:white; padding: 10px; text-align: center;">Freeze</a>&nbsp;', reverse('admin:spaces-freeze',
                                                                                       args=[str(obj.space_id)]))
        else:
            return format_html('<a class="button" href="{}" style="background:#66c2ff; display:block; width:75px; '
                               'height:20px; border-radius:5px; outline:none; border:none; cursor:pointer;'
                               'color:white; padding: 10px; text-align: center;">Unfreeze</a>&nbsp;', reverse('admin:spaces-unfreeze',
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

@admin.register(Order)
class OrderAdmin(ExportMixinAdmin):
    resource_class = OrderResource
    list_display = ("orders_id",
        "order_code",
        "name",
        "company_email",
        "order_time",
        "usage_start_date",
        "usage_end_date",
        "space",
        "amount", 
        "no_of_guest",
        "extras", 
        "hours_booked",
        "days_booked",
        "status",
        "transaction_code",
        "order_type",
        "created_at",
        "expiry_time"
    )

    list_filter = (
        ("order_time", DateRangeFilter), ('order_time', DateTimeRangeFilter), ('order_type')
    )

@admin.register(SpaceType)
class SpaceTypeAdmin(ExportMixinAdmin):
    resource_class = SpaceTypeResource
    list_display = ('space_type', 'space_category')
    list_filter = ('space_category', )

@admin.register(Cancellation)
class CancellationAdmin(ExportMixinAdmin):
    resource_class = CancellationResource
    list_display = ('agent', 'customer', 'booking',
                    'reason', 'status', 'accept', 'reject')
    list_filter = ('status', 'agent__user', )

    def accept(self, obj):
        if obj.status == 'pending':
            return format_html('<a class="button" style="background:#22bb33; width:70px; height:25px; border-radius:25px; outline:none; border:none; cursor:pointer; color:white;" href="{}">Accept</a>', reverse('admin:cancellation-approve', args=[str(obj.cancellation_id)]))
        else:
            return format_html('<a style="text-decoration:none"><button class="btn" style="background:gray; width:70px; height:25px; border-radius:25px; outline:none; border:none; cursor:pointer; color:white;" "  disabled>Accept</button></a>', obj.agent)

    def reject(self, obj):
        if obj.status == 'pending':
            return format_html('<a class="button" style="background:#bb2124; width:70px; height:25px; border-radius:25px; outline:none; border:none; cursor:pointer; color:white;" href="{}">Reject</a>', reverse('admin:cancellation-decline', args=[str(obj.cancellation_id)]))
        else:
            return format_html('<a style="text-decoration:none"><button class="btn" style="background:gray; width:70px; height:25px; border-radius:25px; outline:none; border:none; cursor:pointer; color:white;" disabled>Reject</button></a>', obj.agent)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'approve/<slug:cancellation_id>/',
                self.admin_site.admin_view(self.process_accept),
                name='cancellation-approve',
            ),
            path(
                'decline/<slug:cancellation_id>/',
                self.admin_site.admin_view(self.process_reject),
                name='cancellation-decline',
            ),
        ]
        return custom_urls + urls

    def process_accept(self, request, cancellation_id, *arg, **kwargs):
        cancellation = Cancellation.objects.get(
            cancellation_id=uuid.UUID(cancellation_id))
        order_id = cancellation.booking.orders_id

        CancellationActions(
            cancellation=cancellation).send_approval_email()

        cancellation.status = "accepted"
        cancellation.save()
        
        bookings_with_same_order_id = Order.objects.filter(
            orders_id=order_id).all()

        for booking in bookings_with_same_order_id:
            booking.status = "cancelled"
            booking.save()

        return redirect("admin:api_cancellation_changelist")

    def process_reject(self, request, cancellation_id, *arg, **kwargs):
        cancellation = Cancellation.objects.get(
            cancellation_id=uuid.UUID(cancellation_id))

        CancellationActions(
            cancellation=cancellation).send_decline_email()

        cancellation.status = "rejected"
        cancellation.save()

        return redirect("admin:api_cancellation_changelist")

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass