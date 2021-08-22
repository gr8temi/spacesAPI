from rest_framework.views import APIView
from decouple import config
import calendar
import uuid
import json
import pytz
from datetime import datetime, date, timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import status

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth.models import User

from ..models.user import User
from ..models.agent import Agent
from ..models.spaces import Space
from ..models.order import Order
from ..models.order_type import OrderType
from ..models.availabilities import Availability
from ..helper.helper import order_code
from ..serializers.order import OrderSerializer
from .order import PlaceOrder
from ..permissions.is_agent_permission import UserIsAnAgent

from django.db import transaction, IntegrityError
from ..consumers.channel_layers import notification_creator
from ..signals import subscriber


class ReservationDetail(APIView):
    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def get_object(self, order_code):
        try:
            return Order.objects.get(order_code=order_code)
        except Order.DoesNotExist:
            return Response({"message": "reservation not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, order_code, format=None):
        order = self.get_object(order_code)
        serializer = OrderSerializer(order)
        return Response({"message": "reservation fetched successfully", "payload": serializer.data}, status=status.HTTP_200_OK)


class ReservationList(APIView):
    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def get(self, request, format=None):
        orders = Order.objects.filter(order_type__order_type="reservation")
        serializer = OrderSerializer(orders, many=True)
        return Response({"message": "reservations fetched", "payload": serializer.data}, status=status.HTTP_200_OK)


class PlaceReservation(PlaceOrder):

    def invalid_time(self, date_array):
        invalid_dates = []
        for dates in date_array:
            if datetime.fromisoformat(
                dates["start_date"].replace('Z', '+01:00')) > datetime.fromisoformat(
                    dates["end_date"].replace('Z', '+01:00')):
                invalid_dates.append(dates)
        if invalid_dates:
            return invalid_dates
        else:
            return False

    def reserve_space(self, amount, start_date, end_date, transaction_code, no_of_guest, order_type_name, user, name, email, extras, space_id, duration, hours_booked, order_cde, order_time, order_expiry_time, notes):
    
        order_data = {
            'amount': amount,
            'usage_start_date': start_date,
            'usage_end_date': end_date,
            'status': 'pending',
            'transaction_code': transaction_code,
            'no_of_guest': no_of_guest,
            'order_code': order_cde,
            'order_type': self.get_order_type_id(order_type_name),
            'user': user,
            'name': name,
            'company_email': email,
            'extras': extras,
            'space': space_id,
            'duration': duration,
            'hours_booked': hours_booked,
            'order_time': order_time,
            'expiry_time': order_expiry_time,
            'notes': notes
        }

        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order_serializer.save()

            customer_details = {
                "id": user, "name": name, "email": email}

            return {"payload": {**customer_details, "order_code": order_cde, "Booking start date": start_date, "Booking end date": end_date},
                    "message": f"Order completed", status: True}
        else:
            return {"error": order_serializer.custom_full_errors, status: False}

    def get_active_orders(self, start, space_id):
        orders = Order.objects.filter(space=space_id)
        active_orders = [
            order for order in orders if order.usage_end_date >= start]
        return active_orders

    def check_availability(self, dates_array, model, space, duration):
        space_availability = model.objects.filter(space=space)
        availability = [{'day': av.day, 'all_day': av.all_day, 'open_time': av.open_time,
                         'close_time': av.close_time} for av in space_availability]
        if duration == "hourly":
            opened = []
            for dates in dates_array:
                start_day = calendar.day_name[datetime.fromisoformat(
                    dates["start_date"].replace('Z', '+01:00')).weekday()]
                opening_period = self.check_all_day(availability, start_day)
                if opening_period == True:
                    opened.append({"dates": dates, "opening": "all_day"})
                elif opening_period == False:
                    opened.append({"dates": dates, "opening": "not_opened"})
                elif len(opening_period) > 0:
                    opening = [time.strftime("%m-%d-%Y, %H:%M")
                               for time in opening_period]
                    opened.append({"dates": dates, "opening": opening})

            not_available_dates = []
            for days in opened:
                if days["opening"] != "all_day" and days["opening"] != "not_opened":
                    open_time = datetime.strptime(
                        days["opening"][0], "%m-%d-%Y, %H:%M").hour
                    close_time = datetime.strptime(
                        days["opening"][1], "%m-%d-%Y, %H:%M").hour
                    if open_time > datetime.fromisoformat(
                            days["dates"]["start_date"].replace('Z', '+01:00')).hour or close_time < datetime.fromisoformat(
                            days["dates"]["end_date"].replace('Z', '+01:00')).hour:
                        not_available_dates.append(
                            {"dates": days["dates"], "open_time": open_time, "close_time": close_time})
                elif days["opening"] == "not_opened":
                    start_day = datetime.fromisoformat(
                        days["dates"]["start_date"].replace('Z', '+01:00'))
                    day = calendar.day_name[start_day.weekday()]
                    not_available_dates.append(
                        {"dates": days["dates"], "close_day": day})
            if not_available_dates:
                return not_available_dates
            else:
                return False

    def check_day_difference(self, bookings, duration, now):

        days_not_allowed = []

        for book in bookings:
            start_date = datetime.fromisoformat(
                book["start_date"].replace('Z', '+01:00'))
            end_date = datetime.fromisoformat(
                book["end_date"].replace('Z', '+01:00'))
            if duration == "hourly":
                if start_date < pytz.utc.localize(now):
                    days_not_allowed.append(book)
            elif duration == "daily":
                if start_date.date() < pytz.utc.localize(now).date():
                    days_not_allowed.append(book)
            elif duration == "monthly":
                if start_date.date() < pytz.utc.localize(now).date():
                    days_not_allowed.append(book)

        return days_not_allowed
    # checks for booked dates

    def booked_days(self, start_date, end_date, space_id, duration):
        orders = Order.objects.filter(
            space=space_id).exclude(status="cancelled")

        if duration == "hourly":
            active_orders = [
                order for order in orders if pytz.utc.localize(order.usage_end_date) >= start_date]
        elif duration == "daily" or duration == "monthly":
            active_orders = [
                order for order in orders if pytz.utc.localize(order.usage_end_date).date() >= start_date.date()]
        return active_orders

    def order(self, active_order, start_date, end_date, duration):
        start_date = datetime.fromisoformat(
            start_date.replace('Z', '+01:00'))
        end_date = datetime.fromisoformat(
            end_date.replace('Z', '+01:00'))

        existing = []
        if len(active_order) > 0:

            for order in active_order:

                if duration == "daily":
                    order_start_date = pytz.utc.localize(
                        order.usage_start_date).date()
                    order_end_date = pytz.utc.localize(
                        order.usage_end_date).date()
                    start = start_date.date()
                    end = end_date.date()
                elif duration == "hourly":
                    order_end_date = pytz.utc.localize(order.usage_end_date)
                    order_start_date = pytz.utc.localize(
                        order.usage_start_date)
                    start = start_date
                    end = end_date

                order_type = order.order_type.order_type
                if (start >= order_start_date and start <= order_end_date) or (end <= order_end_date and end >= order_start_date):
                    if order_type == "booking":
                        existing.append(
                            {"start_date": order.usage_start_date, "end_date": order.usage_end_date})
                    elif order_type == "reservation":
                        expiry_time = order.order_time + \
                            timedelta(seconds=21600)

                        existing.append(
                            {"start_date": order.usage_start_date, "end_date": order.usage_end_date, "expiry_time": expiry_time})
                    else:
                        return Response({"message": "Invalid order type"})
                else:
                    return existing
            return existing
        else:
            return existing

    def post(self, request):
        data = request.data
        space_id = data.get("space")
        name = data.get("name")
        email = data.get('company_email')
        space = self.get_space(space_id)
        agent = self.get_agent(space.agent.agent_id)
        agent_name = agent.user.name
        agent_mail = agent.user.email
        notes = data.get("note", "")
        duration = space.duration
        order_cde = order_code()
        existing_bookings = []
        exists = []
        if duration == 'hourly':
            hours_booked = json.loads(json.dumps(data.get("hours_booked")))
            now = datetime.now()
            check = self.check_day_difference(hours_booked, duration, now)

            invalid_time_array = self.invalid_time(hours_booked)
            if invalid_time_array:
                return Response({"message": f"This time is not available ", "payload": {'invalid_time': invalid_time_array}}, status=status.HTTP_400_BAD_REQUEST)
            check_available_array = self.check_availability(
                hours_booked, Availability, space, duration)

            if check:
                return Response({"message": f"You are booking a pass time. kindly book a new date"}, status=status.HTTP_400_BAD_REQUEST)

            if not check_available_array:
                for hours in hours_booked:
                    start_date = datetime.fromisoformat(
                        hours["start_date"].replace('Z', '+01:00'))
                    existing_bookings.extend(self.booked_days(
                        start_date, datetime.fromisoformat(hours["end_date"].replace('Z', '+01:00')), space_id, duration))
            else:
                available_slots = [{"open_time": avail["open_time"],
                                    "close_time":avail["close_time"], "invalid_date":avail["dates"]} for avail in check_available_array if not bool(avail.get("close_day"))]
                available_slots.extend([{"close_day": avail["close_day"], "invalid_date":avail["dates"]}
                                        for avail in check_available_array if bool(avail.get("close_day"))])

                return Response({"message": f"Space does not open before open time, and after close time or close days", "payload": {"dates": available_slots}}, status=status.HTTP_400_BAD_REQUEST)
            for hours in hours_booked:
                ordered = self.order(existing_bookings,
                                     hours["start_date"], hours["end_date"], duration)
                exists.extend(ordered)

        elif duration == "daily" or duration == "monthly":
            days_booked = json.loads(json.dumps(data.get("daily_bookings"))) or json.loads(
                json.dumps(data.get("monthly_bookings")))
            invalid_time_array = self.invalid_time(days_booked)
            # Gets all existing bookings
            now = datetime.now()
            check = self.check_day_difference(days_booked, duration, now)

            if check:
                return Response({"message": f"You are booking a pass time. kindly book a new date"}, status=status.HTTP_400_BAD_REQUEST)

            for days in days_booked:
                start_date = datetime.fromisoformat(
                    days["start_date"].replace('Z', '+01:00')).date()
                existing_bookings.extend(self.booked_days(
                    datetime.fromisoformat(days["start_date"].replace('Z', '+01:00')), datetime.fromisoformat(days["end_date"].replace('Z', '+01:00')), space_id, duration))

            for days in days_booked:

                ordered = self.order(existing_bookings,
                                     days["start_date"], days["end_date"], duration)
                exists.extend(ordered)

        if (bool(exists)):
            if duration == "daily":
                return Response({"message": f"Space is not available on the following days", "payload": days_booked}, status=status.HTTP_409_CONFLICT)
            elif duration == "hourly":
                return Response({"message": f"Space is not available on the following hours", "payload": hours}, status=status.HTTP_409_CONFLICT)
        else:
            if data["user"]:
                user_obj = User.objects.get(user_id=data["user"])
                user = user_obj.user_id
                customer_email = user_obj.email
                customer_name = user_obj.name
            else:
                user = ''
            try:
                with transaction.atomic():
                    order_cde = order_code()
                    order_time = datetime.now()
                    order_expiry_time = order_time + timedelta(hours=24)
                    booked = {}
                    if duration == "daily" or duration == "monthly":
                        booked = days_booked
                    elif duration == "hourly":
                        booked = hours_booked
                    for days in booked:
                        start = datetime.fromisoformat(
                            days['start_date'].replace('Z', '+00:00'))
                        end = datetime.fromisoformat(
                            days['end_date'].replace('Z', '+00:00'))

                        self.reserve_space(data["amount"], start, end, data["transaction_code"], data["no_of_guest"], data["order_type"],
                                           user, data["name"], data["company_email"], data["extras"], data["space"], duration, [], order_cde, order_time, order_expiry_time, notes)
                    # notifications
                    sender = config(
                        "EMAIL_SENDER", default="space.ng@gmail.com")
                    next_day = order_time + timedelta(days=1)
                    # notification for customer booking space
                    subject_customer = "RESERVATION COMPLETE"
                    to_customer = customer_email
                    customer_content = f"Dear {data['name']}, your Reservation has been completed. You reserved space is {space.name} and would expire by {next_day.time()} {next_day.date()}. Thanks for your patronage."

                    # notification for agent that registered space
                    subject_agent = "YOU HAVE A RESERVATION"
                    to_agent = agent_mail
                    agent_content = f"Dear {agent_name}, you have a reservation placed for your space {space.name} listed on our platform. accept the reservation now. Or it would expire by {next_day.time()} {next_day.date()}. "
                    
                    # notification for admin about new reservation
                    all_admin = User.objects.filter(is_super=True)
                    admin_email_list = [admin.email for admin in all_admin if all_admin]
                    subject_admin = "A NEW RESERVATION HAS BEEN MADE"
                    

                    guest_template = get_template('api/order/customer_reservation_notification.html')
                    guest_content = guest_template.render({'guest_name': customer_name, "login_url": f"{config('FRONTEND_URL')}/signin", "space_name":space.name, "space_location":space.address })
                    msg = EmailMultiAlternatives(subject_customer, guest_content, sender, to=[to_customer])
                    msg.attach_alternative(guest_content, "text/html")
                    msg.send()
                    
                    host_template = get_template('api/order/space_host_reservation_notification.html')
                    host_content = host_template.render({'host_name': agent_name, "login_url": f"{config('FRONTEND_URL')}/signin", "space_name":space.name, "space_location":space.address })
                    msg = EmailMultiAlternatives(subject_agent, host_content, sender, to=[to_agent])
                    msg.attach_alternative(host_content, "text/html")
                    msg.send()

                    admin_template = get_template('api/admin/reservation_alert.html')
                    admin_content = admin_template.render({"login_url": f"{config('ADMIN_DASHBOARD_URL')}"})
                    msg = EmailMultiAlternatives(subject_admin, admin_content, sender, to=[admin_email_list])
                    msg.attach_alternative(admin_content, "text/html")
                    msg.send()

                    customer_details = {
                        "id": user, "name": name, "email": email}
                    subscriber.connect(notification_creator)
                    subscriber.send(sender=self.__class__,
                                    data={"user_id": f"{agent.user.user_id}", "notification": f"You have a new Reservation {order_cde} "})
                    return Response(
                        {"payload": {**customer_details, "order_code": order_cde, "Reservation dates": booked},
                            "message": f"Reservation completed Waiting for a response from Space Host"},
                        status=status.HTTP_200_OK)

            except IntegrityError as e:
                return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def approve_reservation(self, orders, data, agent_mail, agent_name, space, customer):
        try:
            with transaction.atomic():
                start_now = datetime.now()
                for order in orders:
                    if order.status == "pending":
                        order.status = "reserved"
                        order.order_time = start_now
                        order.save()
                    else:
                        return Response({"message": "You can't approve this reservation because it's status is not pending"}, status=status.HTTP_400_BAD_REQUEST)
                # notifications
                sender = config(
                    "EMAIL_SENDER", default="space.ng@gmail.com")
                next_day = start_now + timedelta(days=1)
                # notification for customer booking space
                subject_customer = "RESERVATION APPROVED"
                to_customer = customer.email
                customer_content = f"Dear {customer.name}, your Reservation has been Accepted by the space host. You reserved space is {space.name} and would expire by {next_day.time()} {next_day.date()} Remember you can request for extension before it expires. Thanks for your patronage"
                 
                # notification for agent that registered space
                subject_agent = "YOU JUST APPROVED A RESERVATION"
                to_agent = agent_mail
                agent_content = f"Dear {agent_name}, You have approved a reservation for {space.name} listed on our platform. It would expire by {next_day.time()} {next_day.date()}. This expiry is subject to request for extension by the customer "

                guest_template = get_template('api/order/customer_reservation_approved.html')
                guest_content = guest_template.render({'guest_name': customer.name, "login_url": f"{config('FRONTEND_URL')}/signin", "space_name":space.name, "space_location":space.address })
                msg = EmailMultiAlternatives(subject_customer, guest_content, sender, to=[to_customer])
                msg.attach_alternative(guest_content, "text/html")
                msg.send()
                
                # host_template = get_template('api/order/space_host_reservation_approved.html')
                # host_content = host_template.render({'host_name': agent_name, "login_url": f"{config('FRONTEND_URL')}/signin", "space_name":space.name, "space_location":space.address })
                # msg = EmailMultiAlternatives(subject_agent, host_content, sender, to=[to_agent])
                # msg.attach_alternative(host_content, "text/html")
                # msg.send()
                return Response({"message": "Reservation Accepted", "status": f"{order.status}"}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def decline_reservation(self, orders, data, agent_mail, agent_name, space, customer):
        try:
            with transaction.atomic():
                start_now = datetime.now()
                for order in orders:
                    if order.status == "pending":
                        order.status = "cancelled"
                        order.order_time = start_now
                        order.save()
                    else:
                        return Response({"message": "You can't decline this reservation because it's status is not pending"}, status=status.HTTP_400_BAD_REQUEST)
                # notifications
                sender = config(
                    "EMAIL_SENDER", default="space.ng@gmail.com")
                # notification for customer booking space
                subject_customer = "RESERVATION CANCELLED"
                to_customer = customer.email
                customer_content = f"Dear {customer.name}, your Reservation has been Declined by the space host. Kindly book for the space or choose another space for reservation. Thanks for your patronage"

                # notification for agent that registered space
                subject_agent = "YOU JUST DECLINED A RESERVATION"
                to_agent = agent_mail
                agent_content = f"Dear {agent_name}, You have declined a reservation for {space.name} listed on our platform."

                guest_template = get_template('api/order/customer_reservation_denied.html')
                guest_content = guest_template.render({'guest_name': customer.name, "login_url": f"{config('FRONTEND_URL')}/signin", "space_name":space.name, "space_location":space.address })
                msg = EmailMultiAlternatives(subject_customer, guest_content, sender, to=[to_customer])
                msg.attach_alternative(guest_content, "text/html")
                msg.send()
                
                # host_template = get_template('api/order/space_host_reservation_notification.html')
                # host_content = host_template.render({'host_name': agent_name, "login_url": f"{config('FRONTEND_URL')}/signin", "space_name":space.name, "space_location":space.address })
                # msg = EmailMultiAlternatives(subject_agent, host_content, sender, to=[to_agent])
                # msg.attach_alternative(host_content, "text/html")
                # msg.send()
                return Response({"message": "Reservation Declined", "status": f"{order.status}"}, status=status.HTTP_200_OK)

        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def reservation_to_booking(self, orders, data, agent_mail, agent_name, space, transaction_code, customer):
        try:
            with transaction.atomic():
                start_now = datetime.now()
                booking = OrderType.objects.get(order_type="booking")
                for order in orders:
                    if order.status == "pending" or order.status == "reserved" or order.status=="extension":
                        order.status = "booked"
                        order.order_type = booking
                        order.order_time = start_now
                        order.transaction_code = transaction_code
                        order.save()
                # notifications
                sender = config(
                    "EMAIL_SENDER", default="space.ng@gmail.com")
                subject_agent = "A RESERVED SPACE HAS JUST BEEN BOOKED"
                to_agent = [agent_mail]
                agent_content = f"Dear {agent_name}, space {space.name} listed on our platform has been booked."

                subject_customer2 = "BOOKING COMPLETED"
                to_customer = [customer.email]
                customer_content2 = f"Dear {customer.name}\n,Your booking {order.order_code} for {space.name} has been completed.\nThanks for your patronage"

                send_mail(subject_agent, agent_content, sender, to_agent)
                send_mail(subject_customer2, customer_content2,
                          sender, to_customer)

                return Response({"message": "Order completed", "status": f"{order.status}"}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        data = request.data
        user_id = data.get("user")
        update_type = data.get("update_type")
        customer = get_object_or_404(User, user_id=user_id)
        order_code = data.get('order_code')
        transaction_code = data.get('transaction_code')
        try:
            orders = Order.objects.filter(order_code=order_code)
        except:
            return Response({"message": "orders with order code {order_code} not found"}, status=status.HTTP_404_NOT_FOUND)
        space = self.get_space(list(orders)[0].space.space_id)

        # NOTE: create_space endpoint allows the same space to be created more than once, this should be checked!!!
        agent = self.get_agent(space.agent.agent_id)
        agent_mail = agent.user.email
        agent_name = agent.user.name

        if order_code:
            if update_type == "book":
                reserved_to_booking = self.reservation_to_booking(
                    orders, data, agent_mail, agent_name, space, transaction_code, customer)
                return reserved_to_booking
            elif update_type == "approve" or update_type == "decline":
                if request.user.is_authenticated:
                    if update_type == "approve":
                        approve_reservation = self.approve_reservation(
                            orders, data, agent_mail, agent_name, space, customer)
                        return approve_reservation
                    elif update_type == "decline":
                        decline_reservation = self.decline_reservation(
                            orders, data, agent_mail, agent_name, space, customer)
                        return decline_reservation

                else:
                    return Response({"message": "Login as a space host to complete this action."})
            else:
                return Response({"message": "Invalid update type"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Order code not provided"}, status=status.HTTP_400_BAD_REQUEST)


class RequestReservationExtension(PlaceOrder):

    def get(self, request, order_code):
        orders = Order.objects.filter(order_code=order_code)
        if not orders:
            return Response({"message": "We couldn't find any reservations with the given order code"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(orders, many=True)

        return Response({"message": "ex"})

    def post(self, request):
        data = request.data
        reason = data.get("reason")
        order_code = data.get('order_code')
        orders = Order.objects.filter(order_code=order_code)
        if not orders:
            return Response({"message": f"orders with order id {order_code} not found"}, status=status.HTTP_404_NOT_FOUND)

        for order in orders:
            order.status = "extension"
            order.save()
        # user_id = orders[0]
        user_id = list(orders)[0].user.user_id
        customer = get_object_or_404(User, user_id=user_id)
        space = self.get_space(list(orders)[0].space.space_id)
        agent = self.get_agent(space.agent.agent_id)
        agent_mail = agent.user.email
        agent_name = agent.user.name

        try:
            # notifications
            sender = config(
                "EMAIL_SENDER", default="space.ng@gmail.com")

            subject_customer = "REQUEST FOR RESERVATION EXTENSION"
            to_customer = customer.email
            customer_content = f"Dear {customer.name}, you have requested for an extension of time on your reservation. You reserved space is {space.name}. Your request awaits approval of the space host, you will be notified once this is done. Thanks for your patronage."

            # notification for agent that registered space
            subject_agent = "YOU HAVE A REQUEST FOR RESERVATION EXTENSION"
            to_agent = agent_mail
            agent_content = f"Dear {agent_name}, {customer.name} has requested for extension of reservation time for the reason stated below;\n {reason}.\n Approve the extension time or it expires at the previously slated time."

            guest_template = get_template('api/reservation/reservation_extension_guest.html')
            guest_content = guest_template.render({'guest_name': customer.name, "login_url": f"{config('FRONTEND_URL')}/signin"})
            msg = EmailMultiAlternatives(subject_customer, guest_content, sender, to=[to_customer])
            msg.attach_alternative(guest_content, 'text/html')
            msg.send()

            host_template = get_template('api/reservation/reservation_extension_host.html')
            host_content = host_template.render({'host_name': agent_name, 'space_name': space.name, "login_url": f"{config('FRONTEND_URL')}/signin"})
            msg = EmailMultiAlternatives(subject_agent, host_content, sender, to=[to_agent])
            msg.attach_alternative(host_content, 'text/html')
            msg.send()

            subject_admin = "YOU HAVE A NEW REQUEST FOR RESERVATION EXTENSION "
            all_admin = User.objects.filter(is_super=True)
            admin_email_list = [admin.email for admin in all_admin if all_admin]
            admin_template = get_template('api/admin/reservation_extension_alert.html')
            admin_content = admin_template.render(
                {"login_url": f"{config('ADMIN_DASHBOARD_URL')}"}
            )
            msg = EmailMultiAlternatives(
                subject_admin, admin_content, sender, to=admin_email_list
            )
            msg.attach_alternative(admin_content, "text/html")
            msg.send()

            return Response({"message": "Request for extension sent to agent"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "invalid", "err": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def approve_reservation_extension(self, orders, data, agent_mail, agent_name, space, customer):
        # to approve extension time
        try:
            with transaction.atomic():
                start_now = datetime.now()
                for order in orders:
                    if order.status == "extension":
                        order.status = "reserved"
                        order.expiry_time = start_now + timedelta(days=1)
                        order.save()
                    else:
                        return Response({"message": "You can't approve this reservation extension request because it's status is not pending"}, status=status.HTTP_400_BAD_REQUEST)
                # notifications
                sender = config(
                    "EMAIL_SENDER", default="space.ng@gmail.com")
                next_day = start_now + timedelta(days=1)
                # notification for customer booking space
                subject_customer = "EXTENSION FOR RESERVATION APPROVED"
                to_customer = [customer.email]
                customer_content = f"Dear {customer.name}, your request for Reservation extension has been Accepted by the space host. You reserved space is {space.name} and would expire by {next_day.time()} {next_day.date()}. Thanks for your patronage"

                # notification for agent that registered space
                subject_agent = "YOU JUST APPROVED A REQUEST FOR RESERVATION EXTENSION"
                to_agent = [agent_mail]
                agent_content = f"Dear {agent_name}, You have approved a request for reservation extension for {space.name} listed on our platform. It would expire by {next_day.time()} {next_day.date()}."

                guest_template = get_template('api/reservation/extension_approval_guest.html')
                guest_content = guest_template.render({'guest_name': customer.name, 'space_name':space.name, "login_url": f"{config('FRONTEND_URL')}/signin"})
                msg = EmailMultiAlternatives(subject_customer, guest_content, sender, to=[to_customer])
                msg.attach_alternative(guest_content, 'text/html')
                msg.send()

                return Response({"message": "Request for Extension Approved"}, status=status.HTTP_200_OK)

        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def decline_reservation_extension(self, orders, data, agent_mail, agent_name, space, customer):
        try:
            with transaction.atomic():
                start_now = datetime.now()
                for order in orders:
                    if order.status == "extension":
                        if order.expiry_time > start_now:
                            order.status = "reserved"
                            order.save()
                    else:
                        return Response({"message": "You can't decline this reservation extension request because it's status is not extension"}, status=status.HTTP_400_BAD_REQUEST)

                # notifications
                sender = config(
                    "EMAIL_SENDER", default="space.ng@gmail.com")
                # notification for customer
                subject_customer = "REQUEST FOR RESERVATION EXTENSION  DECLINED"
                to_customer = [customer.email]
                customer_content = f"Dear {customer.name}, your  request for extension of Reservation has been Declined by the space host. Kindly proceed to pay before 24hours from your original order time. Thanks for your patronage"

                # notification for agent that registered space
                subject_agent = "YOU JUST DECLINED A REQUEST FOR EXTENSION OF RESERVATION"
                to_agent = [agent_mail]
                agent_content = f"Dear {agent_name}, You have declined a request for extension of reservation for {space.name}listed on our platform."

                # send_mail(subject_agent, agent_content,
                #           sender, to_agent)
                # send_mail(subject_customer, customer_content,
                #           sender, to_customer)
                guest_template = get_template('api/reservation/extension_denial_guest.html')
                guest_content = guest_template.render({'guest_name': customer.name, 'space_name':space.name, "login_url": f"{config('FRONTEND_URL')}/signin"})
                msg = EmailMultiAlternatives(subject_customer, guest_content, sender, to=[to_customer])
                msg.attach_alternative(guest_content, 'text/html')
                msg.send()
                return Response({"message": "Request for Extension Declined"}, status=status.HTTP_200_OK)

        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated, UserIsAnAgent])
    def put(self, request):
        data = request.data
        user_id = data.get("user")
        update_type = data.get("update_type")
        customer = get_object_or_404(User, user_id=user_id)
        order_code = data.get('order_code')
        try:
            orders = Order.objects.filter(order_code=order_code)
        except:
            return Response({"message": "orders with order code {order_code} not found"}, status=status.HTTP_404_NOT_FOUND)
        space = self.get_space(list(orders)[0].space.space_id)

        # NOTE: create_space endpoint allows the same space to be created more than once, this should be checked!!!
        agent = self.get_agent(space.agent.agent_id)
        agent_mail = agent.user.email
        agent_name = agent.user.name
        if order_code:
            if request.user.is_authenticated:
                if update_type == "approve_reservation_extension":
                    approve_extension_request = self.approve_reservation_extension(
                        orders, data, agent_mail, agent_name, space, customer)
                    return approve_extension_request

                elif update_type == "decline_reservation_extension":
                    decline_reservation_extension = self.decline_reservation_extension(
                        orders, data, agent_mail, agent_name, space, customer)
                    return decline_reservation_extension
                else:
                    return Response({"message": "invalid update type"}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({"message": "Login as a space host to complete this action."})
        else:
            return Response({"message": "Order code not provided"}, status=status.HTTP_400_BAD_REQUEST)


# class SingleReservation


class PreviousReservationPerUser(APIView):

    def get(self, request, user_id):
        order_type = OrderType.objects.get(order_type="reservation")
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        reservations = Order.objects.filter(order_type=order_type, user=user)
        now = datetime.now()
        reservations.filter(usage_end_date__lt=now)

        serializer = OrderSerializer(reservations, many=True)

        return Response({"message": "Previous reservation fetched successfully", "payload": serializer.data}, status=status.HTTP_200_OK)


class UpcomingReservationPerUser(APIView):

    def get(self, request, user_id):
        order_type = OrderType.objects.get(order_type="reservation")
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        reservations = Order.objects.filter(order_type=order_type, user=user)
        now = datetime.now()
        reservations.filter(usage_end_date__gt=now)

        serializer = OrderSerializer(reservations, many=True)

        return Response({"message": "Upcoming reservation fetched successfully", "payload": serializer.data}, status=status.HTTP_200_OK)

class ReservationAnalytics(APIView):
    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def get(self, request, agent_id):
        try:
            agent = Agent.objects.get(agent_id=uuid.UUID(agent_id))
        except:
            return Response({"message": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)
        
        str_start_date = request.GET.get('start_date')
        start_date = datetime.fromisoformat(str_start_date.replace('Z', '+00:00'))
        str_end_date = request.GET.get('end_date')
        end_date = datetime.fromisoformat(str_end_date.replace('Z', '+00:00'))

        reservations_within_range = Order.objects.filter(space__agent__agent_id=agent_id, order_type__order_type="reservation", order_time__range=[start_date, end_date])
        no_of_reservations_within_range = len(reservations_within_range)

        return Response({"message": f"Reservations between {start_date} and {end_date} were successfully fetched.", "no_of_reservations": no_of_reservations_within_range}, status=status.HTTP_200_OK)
