from django.apps import apps
from django.contrib import admin
from .models.order import Order
from .models.spaces import Space
from .models.space_type import SpaceType
from .models.spaces_category import SpaceCategory
from .models.agent import Agent
from .models.user import User
from .models.order_type import OrderType
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from import_export.formats import base_formats
from import_export.admin import  ExportMixin
from .resources.order_resource import OrderResource
# from api.models.availabilities import Availability
# models = apps.get_models()

# for model in models:
#     try:
#         admin.site.register(model)
#     except admin.sites.AlreadyRegistered:
#         pass
# admin.site.register(Availability)

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
        ("order_time", DateRangeFilter), ('order_time', DateTimeRangeFilter),
    )


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(SpaceType)
class SpaceTypeAdmin(admin.ModelAdmin):
    list_display = ("space_type",)

@admin.register(SpaceCategory)
class SpaceCategoryAdmin(admin.ModelAdmin):
    list_display = ("space_category","images")

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("user", "business_name")

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("name", "email")

@admin.register(OrderType)
class OrderTypedmin(admin.ModelAdmin):
    list_display = ("order_type",)