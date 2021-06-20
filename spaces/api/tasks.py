from decouple import config
from datetime import timedelta, datetime

from django.utils import timezone
from django.core.mail import send_mail
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.core.mail import send_mail

from celery.task.schedules import crontab
from celery.decorators import periodic_task

from spaces import celery
from spaces.paystack import paystack

from .models.order import Order
from .models.ratings import Rating
from .models.order_type import OrderType
from .models.subscription import SubscriptionPerAgent
from .helper.helper import send_subscription_mail

now = timezone.now()


@periodic_task(
    run_every=(crontab(minute="*/60")), name="update_order_status", ignore_result=False
)
def update_order_status():
    reservations = Order.objects.filter(Q(status="pending") | Q(status="reserved")).filter(order_type__order_type="booking")

    try:
        with transaction.atomic():
            expired_orders_grouped_by_order_code = {}
            for reservation in reservations:
                expiry = reservation.order_time
                if expiry > now:
                    reservation.status = "cancelled"
                    reservation.save()
                if reservation.order_code in expired_orders_grouped_by_order_code:
                    expired_orders_grouped_by_order_code[reservation.order_code].extend(
                        [reservation]
                    )
                else:
                    expired_orders_grouped_by_order_code[reservation.order_code] = [
                        reservation
                    ]
            expiring_array = list(expired_orders_grouped_by_order_code)
            for expiring in expiring_array:
                expire = expired_orders_grouped_by_order_code[expiring]
                user = expired_orders_grouped_by_order_code[expiring][0].user
                agent = expired_orders_grouped_by_order_code[expiring][0].space.agent
                formatted_expiring_bookings_spaces = format_expire_array(expire)
                sender = config("EMAIL_SENDER", default="space.ng@gmail.com")
                # notification for customer reserving space
                subject_customer = "RESERVATION CANCELLED"
                subject_agent = "RESERVATION CANCELLED"
                to_customer = [user.email]
                to_agent = [agent.user.email]
                agent_content = f"Dear {agent.business_name}, Reservations made for \n {formatted_expiring_bookings_spaces}\n has expired and therefore cancelled as the customer did not make neccessary bookings or you didn't approve the reservations on time. "
                customer_content = f"Dear {user.name}, your Reservations for \n {formatted_expiring_bookings_spaces}\n has expired and therefore cancelled. You can rebook the space again "

                send_mail(subject_customer, customer_content, sender, to_customer)
                send_mail(subject_agent, agent_content, sender, to_agent)

    except IntegrityError as e:
        return e.args


def format_expire_array(expire_array):
    dates = ""
    for expire in expire_array:
        dates += f"{expire.space.name} reserved {expire.usage_start_date} {expire.usage_end_date} \n"
    return dates


@periodic_task(
    run_every=(crontab(minute="*/60")),
    name="send_mail_to_almost_expired_reservations",
    ignore_result=False,
)
def send_mail_to_almost_expired_reservations():
    reservations = Order.objects.filter(
        Q(status="reserved") | Q(status="pending") | Q(status="declined")
    )
    almost_expired_two_hours = {}
    almost_expired_one_hour = {}
    for reservation in reservations:
        order_time = reservation.order_time
        now = datetime.now()
        if order_time - now <= timedelta(hours=2):
            if reservation.order_code in almost_expired_two_hours:
                almost_expired_two_hours[reservation.order_code].extend([reservation])
            else:
                almost_expired_two_hours[reservation.order_code] = [reservation]
        elif order_time - now <= timedelta(hours=1):
            if reservation.order_code in almost_expired_one_hour:
                almost_expired_one_hour[reservation.order_code].extend([reservation])
            else:
                almost_expired_one_hour[reservation.order_code] = [reservation]

    expiring_two_hours = list(almost_expired_two_hours)
    expiring_one_hour = list(almost_expired_one_hour)

    for expiring in expiring_two_hours:
        expire_array = almost_expired_two_hours[expiring]
        user_email = almost_expired_two_hours[expiring][0].user.email
        formatted_expiring_bookings_spaces = format_expire_array(expire_array)

        sender = config("EMAIL_SENDER", default="space.ng@gmail.com")
        # notification for customer reserving space
        subject_customer = "RESERVATION COMPLETE"
        to_customer = [user_email]
        customer_content = f"Dear {user_email}, your Reservations for \n {formatted_expiring_bookings_spaces}\n would expire in less than two hours. You can request for extension "

        send_mail(subject_customer, customer_content, sender, to_customer)

    for expiring in expiring_one_hour:
        expire_array = almost_expired_one_hour[expiring]
        user_email = almost_expired_one_hour[expiring][0].user.email
        formatted_expiring_bookings_spaces = format_expire_array(expire_array)

        sender = config("EMAIL_SENDER", default="space.ng@gmail.com")
        # notification for customer reserving space
        subject_customer = "RESERVATION COMPLETE"
        to_customer = [user_email]
        customer_content = f"Dear {user_email}, your Reservations for \n {formatted_expiring_bookings_spaces}\n would expire in less than one hour. You can request for extension "

        send_mail(subject_customer, customer_content, sender, to_customer)


@periodic_task(
    run_every=(crontab(hour="*/12")),
    name="charge_all_expired_subscriptions",
    ignore_result=False,
)
def charge_all_expired_subscriptions():
    expired_subscriptions = SubscriptionPerAgent.objects.filter(
        Q(next_due_date__lte=datetime.now()) & Q(is_cancelled=False)
    )
    successful_subscriptions = []
    unsuccessful_subscriptions = []
    for subscription in expired_subscriptions:
        if subscription.recurring == False:
            agent = subscription.agent
            agent.plan = "commission"
            agent.save()

        auth_code = subscription.authorization_code
        email = subscription.agent.user.email
        amount = subscription.subscription.cost * 100
        payment = paystack.transaction.charge(
            authorization_code=auth_code, email=email, amount=amount
        )
        if payment["status"]:
            subscription.paid = True
            subscription.paid_at = datetime.strptime(
                payment["data"]["transaction_date"].split(".")[0], "%Y-%m-%dT%H:%M:%S"
            )
            subscription.save()
            successful_subscriptions.append(subscription)
        else:
            subscription.paid = False
            subscription.save()
            unsuccessful_subscriptions.append(subscription)

    for subscription in successful_subscriptions:
        email = subscription.agent.user.email
        name = subscription.agent.user.name
        expiry_date = subscription.next_due_date.strftime("%Y-%m-%d, %H:%M:%S")
        subscription_type = subscription.subscription.subscription_type
        subject = "YOUR SUBSCRIPTION IS SUCCESSFULL"
        content = f"Your {subscription_type} has been renewed. And expires on {expiry_date}. Thanks for using our services"

        send_subscription_mail(subject=subject, to=email, name=name, content=content)

    for subscription in unsuccessful_subscriptions:
        agent = subscription.agent
        agent.plan = "commission"
        agent.save()
        email = subscription.agent.user.email
        name = subscription.agent.user.name
        expiry_date = subscription.next_due_date.strftime("%Y-%m-%d, %H:%M:%S")
        subscription_type = subscription.subscription.subscription_type
        subject = "YOUR SUBSCRIPTION COULD NOT BE COMPLETED"
        content = f"Your {subscription_type} could not be completed. Kindly try paying again from your settings page. Meanwhile we have moved you to the commission plan so your access to the services rendered is not cut out. Thanks for using our services"

        send_subscription_mail(subject=subject, to=email, name=name, content=content)

@periodic_task(
    run_every=(crontab(minute="*/720")),
    name="Send mail to for review",
    ignore_result=False,
)
def send_review_message():
    booking = OrderType.objects.get(order_type="booking")
    all_expired_bookings = Order.objects.filter(usage_end_date__lte=datetime.now(), order_type=booking)
    for booking in all_expired_bookings:
        to = booking.user.email
        customer_name = booking.user.name
        space_id = str(booking.space.space_id)
        try:
            Rating.objects.get(order_id__order_id=booking.order_id)
        except Rating.DoesNotExist:
            review_space_url=config("REVIEW_SPACE_URL", default=f"http://localhost:3000/rate")
            subject = "KINDLY HELP REVIEW THE SPACE USED" 
            from_email = config("EMAIL_SENDER", default="space.ng@gmail.com")
            html_content = f"Dear {customer_name} you have successfully used {booking.space.name}. Kindly help review the space at the link below"
            link_message = f'<a href="{review_space_url}/{space_id}/{booking.order_id}">Review space</a>'
            send_mail(subject, html_content, from_email, [to], fail_silently=False, html_message=link_message)
