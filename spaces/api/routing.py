from django.urls import path

from .consumers.notification import NotificationConsumer


websocket_urlpatterns = [
    path('ws/v1/notify/<str:user_id>/',  NotificationConsumer),
]
