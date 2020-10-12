from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.dispatch import receiver
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from ..models import order
from ..signals import subscriber
from ..views.booking import BookingView
import json
from ..models.notification import Notification
from ..serializers.notification import NotificationSerializer

def filtered_notifications(user_id):
    # return serialize('json', Notification.objects.filter(
    #     user_id=user_id))
    notifications = NotificationSerializer(Notification.objects.filter(user_id=user_id),many=True)
    return notifications.data

def change_read_property(notification_id,operation):

    notification = get_object_or_404(Notification,notification_id=notification_id)
    notification.read = True
    notification.save()
    return notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}_group'

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

        self.notifications = await database_sync_to_async(filtered_notifications)(self.user_id)
        await self.channel_layer.group_send(
            self.user_group_name,
            {
                'type': 'notification',
                'data': {
                    "text": "Notification",
                    "notification": self.notifications}
            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        notification_id = data['notification_id']
        operation = data["operation"]
        await database_sync_to_async(change_read_property)(notification_id,operation)
        return

     # Receive message from room group
    async def notification(self, event):
        notification = event['data']

        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'notification': notification
        }))
