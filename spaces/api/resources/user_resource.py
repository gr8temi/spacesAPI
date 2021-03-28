from import_export import resources
from api.models.user import User

class UserResource(resources.ModelResource):
    class Meta:
        model = User
