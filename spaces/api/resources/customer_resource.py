from import_export import resources
from api.models.customer import Customer

class CustomerResource(resources.ModelResource):
    class Meta:
        model = Customer
