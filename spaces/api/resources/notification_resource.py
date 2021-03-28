from import_export import resources
from api.models.notification import Notification

class NotificationResource(resources.ModelResource):
    class Meta:
        model = Notification
