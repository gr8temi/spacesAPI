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
from .models.spaces_category import SpaceCategory
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .resources.order_resource import OrderResource
from .resources.space_category_resource import SpaceCategoryResource
from .models.ratings import Rating
from .resources.rating_resource import RatingResource
from .models.subscription import SubscriptionPerAgent
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .resources.order_resource import OrderResource
from .resources.order_type_resource import OrderTypeResource
from .resources.space_type_resource import SpaceTypeResource
from .resources.subscription_per_agent_resource import SubscriptionPerAgentResource
from .models.subscription import Subscription
from .models.refund import Refund
from .resources.refund_resource import RefundResource
from .resources.subscription_resource import SubscriptionResource
from .resources.user_resource import UserResource
from django.utils.safestring import mark_safe

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
                    'capacity', 'amount', 'space_host', 'space_host_business_name', 'duration', 'carspace', 'rules', 'cancellation_rule', 'ratings',
                    'active', 'freeze_btn')
    list_filter = ['agent']
    search_fields = ['name']

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
                               'color:white; padding: 10px 10px 5px; text-align: center;">FREEZE</a>&nbsp;', reverse('admin:spaces-freeze',
                                                                                       args=[str(obj.space_id)]))
        else:
            return format_html('<a class="button" href="{}" style="background: #ff6666; display:block; width:75px; '
                               'height:20px; border-radius:5px; outline:none; border:none; cursor:pointer;'
                               'color:white; padding: 10px 10px 5px; text-align: center;">UNFREEZE</a>&nbsp;', reverse('admin:spaces-unfreeze',
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
    def booking_code(self, obj):
        return obj.order_code
    booking_code.short_description = "Booking Code"

    def customer_name(self, obj):
        return obj.name
    customer_name.short_description = "Customer Name"

    def customer_email(self, obj):
        return obj.company_email
    customer_email.short_description = "Customer Email"

    def create_date(self, obj):
        return obj.created_at
    create_date.short_description = "Create Date"

    def start_date(self, obj):
        return obj.usage_start_date
    start_date.short_description = "Start Date"

    def end_date(self, obj):
        return obj.usage_end_date
    end_date.short_description = "End Date"

    def space_host_business_name(self, obj):
        return obj.space
    space_host_business_name.short_description = "Space Host Business Name"

    def space_host(self, obj):
        return obj.agent_name()
    space_host.short_description = "Space Host"

    def bank_name(self, instance):
        return instance.space.agent.bank
    bank_name.short_description = "Bank Name"

    def account_number(self, instance):
        return instance.space.agent.account_number
    account_number.short_description = "Account Number"

    def billing_preference(self, instance):
        return instance.space.agent.plans
    billing_preference.short_description = "Billing Preference"

    resource_class = OrderResource
    list_display = ("orders_id",
        "booking_code",
        "customer_name",
        "customer_email",
        "create_date",
        "start_date",
        "end_date",
        "space_host",
        "space_host_business_name",
        "bank_name",
        "account_number",
        "billing_preference",
        "amount"
    )

    list_filter = (
        ("created_at", DateRangeFilter), ("created_at", DateTimeRangeFilter)
    )
    def get_rangefilter_created_at_title(self, request, field_path):
        return 'Create Date'

@admin.register(Refund)
class RefundAdmin(ExportMixinAdmin):
    resource_class = RefundResource
    list_display = ('customer', 'order_code', 'order_name', 'space', 'space_host', 'space_host_business_name')
    list_filter = ('space', 'user')

@admin.register(Subscription)
class SubscriptionAdmin(ExportMixinAdmin):
    resource_class = SubscriptionResource
    list_display = ('subscription_name', 'subscription_type', 'subscription_plan', 'cost')
    list_filter = ('subscription_title', 'subscription_type', 'subscription_plan')

@admin.register(SubscriptionPerAgent)
class SubscriptionPerSpaceHostAdmin(ExportMixinAdmin):
    resource_class = SubscriptionPerAgentResource
    list_display = ('space_host', 'agent', 'subscription_name', 'amount', 'recurring', 'next_due_date', 'paid', 'paid_at', 'is_cancelled', 'reference_code', 'authorization_code',)
    list_filter = ('subscription', 'agent')

@admin.register(SpaceType)
class SpaceTypeAdmin(ExportMixinAdmin):
    resource_class = SpaceTypeResource
    list_display = ('space_type', 'space_category')
    list_filter = ('space_category', )

@admin.register(Rating)
class RatingAdmin(ExportMixinAdmin):
    resource_class = RatingResource
    list_display = ('space_name', 'space_type', 'space_host', 'space_host_business_name', 'rating', 'comment',)
    list_filter = ('space', 'user')

@admin.register(OrderType)
class OrderTypeAdmin(ExportMixinAdmin):
    resource_class = OrderTypeResource
    list_display = ('order_type_id', 'order_type')


@admin.register(User)
class UserAdmin(ExportMixinAdmin):
    resource_class = UserResource
    list_display = ('name', 'email', 'phone_number', 'date_of_birth', 'social_links', 'profile_url',
                    'email_verified', 'is_super', 'is_customer', 'is_agent', 'is_active', 'token')
    list_filter = ('email_verified', 'is_super', 'is_customer', 'is_agent', 'is_active')

@admin.register(SpaceCategory)
class SpaceCategoryAdmin(ExportMixinAdmin):
    resource_class = SpaceCategoryResource
    list_display = ('category',)
    list_filter = ('space_category', )

@admin.register(Cancellation)
class CancellationAdmin(ExportMixinAdmin):
    resource_class = CancellationResource
    list_display = ('customer', 'space_host', 'agent', 'booking','cancellation_rule',
                    'reason', 'status', 'accept', 'reject')
    list_filter = ('status', 'agent', 'customer',  )
    
    def cancellation_rule(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:api_cancellationrules_change", args=(obj.booking.cancellation_policy,)),
            obj.booking.cancellation_policy
        ))
    cancellation_rule.short_description = 'Cancellation Policy'

    def accept(self, obj):
        if obj.status == 'pending':
            return format_html('<a class="button" style="text-decoration:none; display:block; background:#22bb33; width:60px; padding-top:6px; text-align:center; height:17px; border-radius:25px; outline:none; border:none; cursor:pointer; color:white;" href="{}">ACCEPT</a>', reverse('admin:cancellation-approve', args=[str(obj.cancellation_id)]))
        else:
            return format_html('<a style="text-decoration:none"><button class="btn" style="background:gray; width:70px; height:27px; font-size: 12px; padding-top:2px; border-radius:25px; outline:none; border:none; cursor:pointer; color:white; pointer-events:none;" disabled>ACCEPT</button></a>', obj.agent)

    def reject(self, obj):
        if obj.status == 'pending':
            return format_html('<a class="button" style="text-decoration:none; display:block; background:#bb2124; width:60px; padding-top:6px; text-align:center; height:17px; border-radius:25px; outline:none; border:none; cursor:pointer; color:white;" href="{}">REJECT</a>', reverse('admin:cancellation-decline', args=[str(obj.cancellation_id)]))
        else:
            return format_html('<a style="text-decoration:none"><button class="btn" style="background:gray; width:70px; height:27px; font-size: 12px; padding-top:2px; border-radius:25px; outline:none; border:none; cursor:pointer; color:white; pointer-events:none;" disabled>REJECT</button></a>', obj.agent)

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
