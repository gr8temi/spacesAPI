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
from django.urls import path
from django.shortcuts import redirect


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


for model in models:
    try:
        if model is not Cancellation:
            admin.site.register(model)

        else:
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

    except admin.sites.AlreadyRegistered:
        pass
# admin.site.register(Availability)
