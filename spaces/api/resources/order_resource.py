from import_export import resources
from ..models.order import Order

class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = ("orders_id",
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
        export_order = ("orders_id",
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