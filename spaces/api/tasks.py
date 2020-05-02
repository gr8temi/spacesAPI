from celery.task.schedules import crontab
from celery.decorators import periodic_task
from spaces import celery
from .models.order import Order
from django.utils import timezone
from datetime import timedelta


now = timezone.now()

@periodic_task(run_every=(crontab(minute='*/15')), name="update_order_status", ignore_result=False)
def update_order_status():
    reservations = Order.objects.filter(status="pending")
    for reservation in reservations:
        expiry = reservation.order_time + timedelta(seconds=21600)
        if expiry > now:
            order.status = "failed"
