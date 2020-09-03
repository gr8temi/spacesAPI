from django.dispatch import receiver
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..signals import subscriber

from ..models.notification import Notification
from ..serializers.notification import NotificationSerializer

def notification_creator(sender, **kwargs):
    data = kwargs["data"]
    notification = data["notification"]
    Notification.objects.create(
        notification=notification, user_id=data["user_id"])


@receiver(post_save, sender=Notification)
def send_notification(sender, instance, **kwargs):
    layer = get_channel_layer()
    group_name = f"user_{instance.user_id}_group"
    notifications = NotificationSerializer(Notification.objects.filter(user_id=instance.user_id), many=True).data
    async_to_sync(layer.group_send)(
        group_name,
        {
            'type': 'notification',
            'data': {
                'text': 'Notification',
                'notification': notifications,
            }
        }
    )
