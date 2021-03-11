from import_export import resources
from import_export.fields import Field
from ..models.order import Order

class OrderResource(resources.ModelResource):
    orders_id = Field(attribute="orders_id", column_name="Order ID")
    order_code = Field(attribute="order_code", column_name="Booking Code")
    name = Field(attribute="name", column_name="Customer Name")
    company_email = Field(attribute="company_email", column_name="Customer Email")
    created_at = Field(attribute="created_at", column_name="Create Date")
    usage_start_date = Field(attribute="usage_start_date", column_name="Start Date")
    usage_end_date = Field(attribute="usage_end_date", column_name="End Date")
    space = Field(attribute="space", column_name="Business Name")
    space_host = Field(attribute="agent_name", column_name="Space Host")
    bank_name = Field(column_name="Bank Name")
    account_number = Field(column_name="Account Number")
    billing_preference = Field(column_name="Billing Preference")
    amount = Field(attribute="amount", column_name="Amount")


    def dehydrate_bank_name(self, instance):
        return instance.space.agent.bank

    def dehydrate_account_number(self, instance):
        return instance.space.agent.account_number

    def dehydrate_billing_preference(self, instance):
        return instance.space.agent.plans

    class Meta:
        model = Order
        fields = ("orders_id",
        "order_code",
        "name",
        "company_email",
        "created_at",
        "usage_start_date",
        "usage_end_date",
        "space",
        "space_host",
        "bank_name",
        "account_number",
        "billing_preference",
        "amount"
    )
