from celery.task.schedules import crontab
from celery.decorators import periodic_task
from spaces import celery
from .models.order import Order
from django.utils import timezone
from datetime import timedelta, datetime
from decouple import config
from django.core.mail import send_mail
from django.db.models import Q
from django.db import transaction, IntegrityError
now = timezone.now()


@periodic_task(run_every=(crontab(minute='*/60')), name="update_order_status", ignore_result=False)
def update_order_status():
    reservations = Order.objects.filter(
        Q(status="pending") | Q(status="reserved"))

    try:
        with transaction.atomic():
            expired_orders_grouped_by_order_code = {}
            for reservation in reservations:
                expiry = reservation.order_time
                if expiry > now:
                    reservation.status = "cancelled"
                    reservation.save()
                if reservation.order_code in expired_orders_grouped_by_order_code:
                    expired_orders_grouped_by_order_code[reservation.order_code].extend([
                                                                                        reservation])
                else:
                    expired_orders_grouped_by_order_code[reservation.order_code] = [
                        reservation]
            expiring_array = list(expired_orders_grouped_by_order_code)
            for expiring in  expiring_array:
                expire = expired_orders_grouped_by_order_code[expiring]
                user = expired_orders_grouped_by_order_code[expiring][0].user
                agent = expired_orders_grouped_by_order_code[expiring][0].space.agent
                formatted_expiring_bookings_spaces = format_expire_array(
                    expire)
                sender = config(
                    "EMAIL_SENDER", default="space.ng@gmail.com")
                # notification for customer reserving space
                subject_customer = "RESERVATION CANCELLED"
                subject_agent = "RESERVATION CANCELLED"
                to_customer = [user.email]
                to_agent = [agent.user.email]
                agent_content = f"Dear {agent.business_name}, Reservations made for \n {formatted_expiring_bookings_spaces}\n has expired and therefore cancelled as the customer did not make neccessary bookings or you didn't approve the reservations on time. "
                customer_content = f"Dear {user.name}, your Reservations for \n {formatted_expiring_bookings_spaces}\n has expired and therefore cancelled. You can rebook the space again "

                send_mail(subject_customer, customer_content,
                        sender, to_customer)
                send_mail(subject_agent, agent_content,
                          sender, to_agent)

    except IntegrityError as e:
        return e.args


def format_expire_array(expire_array):
    dates = ""
    for expire in expire_array:
        dates += f"{expire.space.name} reserved {expire.usage_start_date} {expire.usage_end_date} \n"
    return dates


@periodic_task(run_every=(crontab(minute='*/60')), name="send_mail_to_almost_expired_reservations", ignore_result=False)
def send_mail_to_almost_expired_reservations():
    reservations = Order.objects.filter(
        Q(status="reserved") | Q(status="pending"))
    almost_expired_two_hours = {}
    almost_expired_one_hour = {}
    for reservation in reservations:
        order_time = reservation.order_time
        now = datetime.now()
        if order_time - now <= timedelta(hours=2):
            if reservation.order_code in almost_expired_two_hours:
                almost_expired_two_hours[reservation.order_code].extend([
                                                                        reservation])
            else:
                almost_expired_two_hours[reservation.order_code] = [
                    reservation]
        elif order_time - now <= timedelta(hours=1):
            if reservation.order_code in almost_expired_one_hour:
                almost_expired_one_hour[reservation.order_code].extend([
                    reservation])
            else:
                almost_expired_one_hour[reservation.order_code] = [
                    reservation]

    expiring_two_hours = list(almost_expired_two_hours)
    expiring_one_hour = list(almost_expired_one_hour)

    for expiring in expiring_two_hours:
        expire_array = almost_expired_two_hours[expiring]
        user_email = almost_expired_two_hours[expiring][0].user.email
        formatted_expiring_bookings_spaces = format_expire_array(expire_array)

        sender = config(
            "EMAIL_SENDER", default="space.ng@gmail.com")
        # notification for customer reserving space
        subject_customer = "RESERVATION COMPLETE"
        to_customer = [user_email]
        customer_content = f"Dear {user_email}, your Reservations for \n {formatted_expiring_bookings_spaces}\n would expire in less than two hours. You can request for extension "

        send_mail(subject_customer, customer_content,
                  sender, to_customer)

    for expiring in expiring_one_hour:
        expire_array = almost_expired_one_hour[expiring]
        user_email = almost_expired_one_hour[expiring][0].user.email
        formatted_expiring_bookings_spaces = format_expire_array(expire_array)

        sender = config(
            "EMAIL_SENDER", default="space.ng@gmail.com")
        # notification for customer reserving space
        subject_customer = "RESERVATION COMPLETE"
        to_customer = [user_email]
        customer_content = f"Dear {user_email}, your Reservations for \n {formatted_expiring_bookings_spaces}\n would expire in less than one hour. You can request for extension "

        send_mail(subject_customer, customer_content,
                  sender, to_customer)
