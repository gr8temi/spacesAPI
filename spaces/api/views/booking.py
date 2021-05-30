import json
import uuid
import pytz
from pytz import timezone as py_timezone
import calendar
import time
from datetime import date, timedelta, datetime
from decouple import config

from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth.models import User

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..models.spaces import Space
from ..models.order import Order
from ..models.agent import Agent
from ..models.customer import Customer
from ..models.user import User
from ..models.order_type import OrderType
from ..models.cancelation import Cancellation
from ..models.availabilities import Availability

from ..helper.helper import order_code

from ..serializers.order import OrderSerializer, OrdersFetchSerializer
from ..serializers.user import UserSerializer
from ..serializers.cancelation import (
    CancellationSerializer,
    CancellationFetchSerializer,
)

from ..consumers.channel_layers import notification_creator
from ..signals import subscriber

from ..permissions.is_agent_permission import UserIsAnAgent
from .order import PlaceOrder

lagos = py_timezone("Africa/Lagos")


def send_booking_mail(customer_email, agent_mail, customer_name, agent_name, space):
    sender = config("EMAIL_SENDER", default="space.ng@gmail.com")

    # notification for customer booking space
    subject_customer = "BOOKING COMPLETE"
    to_customer = customer_email
    # customer_content = f"Dear {to_customer}, your Booking has been completed"

    # notification for agent that registered space
    subject_agent = "YOU HAVE A BOOKING"
    to_agent = agent_mail
    # agent_content = f"Dear {agent_name}, you have a booking placed for your space {space.name} listed on our platform."

    # notification for admin about customer booking space
    subject_admin = "A NEW BOOKING HAS BEEN MADE"
    all_admin = User.objects.filter(is_super=True)
    admin_email_list = [admin.email for admin in all_admin if all_admin]

    guest_template = get_template("api/order/customer_booking_notification.html")
    guest_content = guest_template.render(
        {
            "guest_name": customer_name,
            "login_url": f"{config('FRONTEND_URL')}/signin",
            "space_name": space.name,
            "space_location": space.address,
        }
    )
    msg = EmailMultiAlternatives(
        subject_customer, guest_content, sender, to=[to_customer]
    )
    msg.attach_alternative(guest_content, "text/html")
    msg.send()

    host_template = get_template("api/order/space_host_booking_notification.html")
    host_content = host_template.render(
        {
            "host_name": agent_name,
            "login_url": f"{config('FRONTEND_URL')}/signin",
            "space_name": space.name,
            "space_location": space.address,
        }
    )
    msg = EmailMultiAlternatives(subject_agent, host_content, sender, to=[to_agent])
    msg.attach_alternative(host_content, "text/html")
    msg.send()

    admin_template = get_template("api/admin/booking_alert.html")
    admin_content = admin_template.render(
        {"login_url": f"{config('FRONTEND_URL')}/signin"}
    )
    msg = EmailMultiAlternatives(
        subject_admin, admin_content, sender, to=admin_email_list
    )
    msg.attach_alternative(admin_content, "text/html")
    msg.send()


class BookingStatus(APIView):
    def get_order(self, order_code):

        try:
            return Order.objects.get(order_code=order_code)
        except:
            return False

    def get(self, request, order_code):

        order = self.get_order(order_code)

        if order:
            order_type = order.order_type
            serializer = OrderSerializer(order)
            if str(order_type) == "booking":
                return Response(
                    {
                        "message": "Booking fetched successfully",
                        "payload": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )


class BookingView(PlaceOrder):
    def invalid_time(self, date_array):
        invalid_dates = []
        for dates in date_array:
            if datetime.fromisoformat(
                dates["start_date"].replace("Z", "+00:00")
            ) > datetime.fromisoformat(dates["end_date"].replace("Z", "+00:00")):
                invalid_dates.append(dates)
        if invalid_dates:
            return invalid_dates
        else:
            return False

    def book_space(
        self,
        amount,
        start_date,
        end_date,
        transaction_code,
        no_of_guest,
        order_type_name,
        user,
        name,
        email,
        extras,
        space_id,
        duration,
        hours_booked,
        order_cde,
        order_time,
        booking_type,
        notes,
        offline_booking,
    ):
        space = Space.objects.get(space_id=space_id)
        space_cost = space.amount
        space_cancellation_policy = space.cancellation_rule
        booking_amount = 0
        if duration == "hourly":
            hour_difference = int((end_date - start_date).total_seconds() / (3600 * 60))
            if hour_difference == 0:
                hour_difference = 1
            booking_amount = hour_difference * space_cost
        elif duration == "daily":
            day_difference = (end_date - start_date).days
            booking_amount = day_difference * space_cost
        elif duration == "monthly":
            month_difference = (end_date.year - start_date.year) * 12 + (
                end_date.month - start_date.month
            )
            booking_amount = month_difference * space_cost

        extra_sum = 0
        for extra in extras:
            extra_sum += float(extra.get("amount"))
        print(booking_amount, extra_sum)

        booking_amount = (booking_amount + extra_sum) 
        print(booking_amount)
        order_data = {
            "amount": booking_amount,
            "usage_start_date": start_date,
            "usage_end_date": end_date,
            "status": "pending",
            "transaction_code": transaction_code,
            "no_of_guest": no_of_guest,
            "order_code": order_cde,
            "order_type": f"{booking_type}",
            "user": user,
            "name": name,
            "company_email": email,
            "extras": extras,
            "space": space_id,
            "duration": duration,
            "hours_booked": hours_booked,
            "order_time": order_time,
            "cancellation_rule": space_cancellation_policy,
            "notes": notes,
            "offline_booking": offline_booking,
        }
        print(order_data)

        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order_serializer.save()

            customer_details = {"id": user, "name": name, "email": email}

            return {
                "payload": {
                    **customer_details,
                    "order_code": order_cde,
                    "Booking start date": start_date,
                    "Booking end date": end_date,
                },
                "message": f"Order completed",
                status: True,
            }
        else:
            return {"error": order_serializer.custom_full_errors, status: False}

    def get_active_orders(self, start, space_id):
        orders = Order.objects.filter(space=space_id)
        active_orders = [order for order in orders if order.usage_end_date >= start]
        return active_orders

    def check_availability(self, dates_array, model, space, duration):
        space_availability = model.objects.filter(space=space)
        availability = [
            {
                "day": av.day,
                "all_day": av.all_day,
                "open_time": av.open_time,
                "close_time": av.close_time,
            }
            for av in space_availability
        ]
        if duration == "hourly":
            opened = []
            for dates in dates_array:
                start_day = calendar.day_name[
                    datetime.fromisoformat(
                        dates["start_date"].replace("Z", "+00:00")
                    ).weekday()
                ]
                opening_period = self.check_all_day(availability, start_day)
                if opening_period == True:
                    opened.append({"dates": dates, "opening": "all_day"})
                elif opening_period == False:
                    opened.append({"dates": dates, "opening": "not_opened"})
                elif len(opening_period) > 0:
                    opening = [
                        time.strftime("%m-%d-%Y, %H:%M") for time in opening_period
                    ]
                    opened.append({"dates": dates, "opening": opening})

            not_available_dates = []
            for days in opened:
                if days["opening"] != "all_day" and days["opening"] != "not_opened":
                    open_time = datetime.strptime(
                        days["opening"][0], "%m-%d-%Y, %H:%M"
                    ).hour
                    close_time = datetime.strptime(
                        days["opening"][1], "%m-%d-%Y, %H:%M"
                    ).hour
                    if (
                        open_time
                        > datetime.fromisoformat(
                            days["dates"]["start_date"].replace("Z", "+00:00")
                        ).hour
                        or close_time
                        < datetime.fromisoformat(
                            days["dates"]["end_date"].replace("Z", "+00:00")
                        ).hour
                    ):
                        not_available_dates.append(
                            {
                                "dates": days["dates"],
                                "open_time": open_time,
                                "close_time": close_time,
                            }
                        )
                elif days["opening"] == "not_opened":
                    start_day = datetime.fromisoformat(
                        days["dates"]["start_date"].replace("Z", "+00:00")
                    )
                    day = calendar.day_name[start_day.weekday()]
                    not_available_dates.append(
                        {"dates": days["dates"], "close_day": day}
                    )
            if not_available_dates:
                return not_available_dates
            else:
                return False

    def check_day_difference(self, bookings, duration, now):

        days_not_allowed = []

        for book in bookings:
            start_date = datetime.fromisoformat(
                book["start_date"].replace("Z", "+00:00")
            )
            end_date = datetime.fromisoformat(book["end_date"].replace("Z", "+00:00"))
            if duration == "hourly":
                if start_date < lagos.localize(now):
                    days_not_allowed.append(book)
            elif duration == "daily":
                if start_date.date() < lagos.localize(now).date():
                    days_not_allowed.append(book)
            elif duration == "monthly":
                # if (end_date.date() - start_date.date()).days < 28 or (end_date.date() - start_date.date()).days > 31:
                #     return Response({"message": "The time different in your booking is not up to a monthly difference"}, status=status.HTTP_400_BAD_REQUEST)
                if start_date.date() < lagos.localize(now).date():
                    days_not_allowed.append(book)

        return days_not_allowed

    def booked_days(self, start_date, end_date, space_id, duration):
        orders = Order.objects.filter(space=space_id).exclude(status="cancelled")

        if duration == "hourly":
            active_orders = [
                order
                for order in orders
                if lagos.localize(order.usage_end_date) >= start_date
            ]
        elif duration == "daily" or duration == "monthly":
            active_orders = [
                order
                for order in orders
                if lagos.localize(order.usage_end_date).date() >= start_date.date()
            ]
        return active_orders

    def order(self, active_order, start_date, end_date, duration):
        start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

        existing = []
        if len(active_order) > 0:

            for order in active_order:

                if duration == "daily" or duration == "monthly":
                    order_start_date = lagos.localize(order.usage_start_date).date()
                    order_end_date = lagos.localize(order.usage_end_date).date()
                    start = start_date.date()
                    end = end_date.date()
                elif duration == "hourly":
                    order_end_date = lagos.localize(order.usage_end_date)
                    order_start_date = lagos.localize(order.usage_start_date)
                    start = start_date
                    end = end_date

                order_type = order.order_type.order_type
                if (start >= order_start_date and start <= order_end_date) or (
                    end <= order_end_date and end >= order_start_date
                ):
                    if order_type == "booking":
                        existing.append(
                            {
                                "start_date": order.usage_start_date,
                                "end_date": order.usage_end_date,
                            }
                        )
                    elif order_type == "booking":
                        expiry_time = order.order_time + timedelta(seconds=21600)

                        existing.append(
                            {
                                "start_date": order.usage_start_date,
                                "end_date": order.usage_end_date,
                                "expiry_time": expiry_time,
                            }
                        )
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
        email = data.get("company_email")
        offline_booking = data.get("offline_booking", False)
        try:
            space = Space.objects.get(space_id=space_id)

        except Exception as err:
            return Response(
                {"message": "Space not found"}, status=status.HTTP_404_NOT_FOUND
            )

        agent = Agent.objects.get(agent_id=space.agent.agent_id)

        duration = space.duration
        order_cde = order_code()
        existing_bookings = []
        exists = []
        if duration == "hourly":
            hours_booked = json.loads(json.dumps(data.get("hours_booked")))
            now = datetime.now()
            check = self.check_day_difference(hours_booked, duration, now)

            invalid_time_array = self.invalid_time(hours_booked)
            if invalid_time_array:
                return Response(
                    {
                        "message": f"This time is not available ",
                        "payload": {"invalid_time": invalid_time_array},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            check_available_array = self.check_availability(
                hours_booked, Availability, space, duration
            )

            if check:
                return Response(
                    {"message": f"You are booking a pass time. kindly book a new date"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not check_available_array:
                for hours in hours_booked:
                    start_date = datetime.fromisoformat(
                        hours["start_date"].replace("Z", "+00:00")
                    )
                    print(start_date.hour)
                    existing_bookings.extend(
                        self.booked_days(
                            start_date,
                            datetime.fromisoformat(
                                hours["end_date"].replace("Z", "+00:00")
                            ),
                            space_id,
                            duration,
                        )
                    )
            else:
                available_slots = [
                    {
                        "open_time": avail["open_time"],
                        "close_time": avail["close_time"],
                        "invalid_date": avail["dates"],
                    }
                    for avail in check_available_array
                    if not bool(avail.get("close_day"))
                ]
                available_slots.extend(
                    [
                        {
                            "close_day": avail["close_day"],
                            "invalid_date": avail["dates"],
                        }
                        for avail in check_available_array
                        if bool(avail.get("close_day"))
                    ]
                )

                return Response(
                    {
                        "message": f"Space does not open before open time, and after close time or close days",
                        "payload": {"dates": available_slots},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            for hours in hours_booked:
                ordered = self.order(
                    existing_bookings, hours["start_date"], hours["end_date"], duration
                )
                exists.extend(ordered)

        elif duration == "daily" or duration == "monthly":
            days_booked = json.loads(
                json.dumps(data.get("daily_bookings"))
            ) or json.loads(json.dumps(data.get("monthly_bookings")))
            invalid_time_array = self.invalid_time(days_booked)
            # Gets all existing bookings
            now = datetime.now()
            check = self.check_day_difference(days_booked, duration, now)
            if check:
                if duration == "daily" or duration == "hourly":
                    return Response(
                        {
                            "message": f"You are booking a pass date. kindly book a new date"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    return Response(
                        {
                            "message": f"You are booking a pass month. kindly book a new date"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            for days in days_booked:
                start_date = datetime.fromisoformat(
                    days["start_date"].replace("Z", "+00:00")
                ).date()
                existing_bookings.extend(
                    self.booked_days(
                        datetime.fromisoformat(
                            days["start_date"].replace("Z", "+00:00")
                        ),
                        datetime.fromisoformat(days["end_date"].replace("Z", "+00:00")),
                        space_id,
                        duration,
                    )
                )

            for days in days_booked:

                ordered = self.order(
                    existing_bookings, days["start_date"], days["end_date"], duration
                )
                exists.extend(ordered)

        if bool(exists):
            if duration == "daily":
                return Response(
                    {
                        "message": f"Space is not available on the following days",
                        "payload": days_booked,
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            elif duration == "hourly":
                return Response(
                    {
                        "message": f"Space is not available on the following hours",
                        "payload": hours,
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            elif duration == "monthly":
                return Response(
                    {
                        "message": f"Space is not available on the following month",
                        "payload": days_booked,
                    },
                    status=status.HTTP_409_CONFLICT,
                )
        else:
            if data["user"]:
                user = User.objects.get(user_id=data["user"]).user_id
                customer_email = User.objects.get(user_id=data["user"]).email
            else:
                user = ""
            try:
                with transaction.atomic():
                    order_cde = order_code()
                    order_time = datetime.now()
                    if duration == "daily" or duration == "monthly":
                        booked = days_booked
                    elif duration == "hourly":
                        booked = hours_booked
                    booking_type = self.get_order_type_id(data["order_type"])
                    booking_error = ""
                    for days in booked:
                        start = datetime.fromisoformat(
                            days["start_date"].replace("Z", "+00:00")
                        )
                        end = datetime.fromisoformat(
                            days["end_date"].replace("Z", "+00:00")
                        )

                        booking = self.book_space(
                            data["amount"],
                            start,
                            end,
                            data["transaction_code"],
                            data["no_of_guest"],
                            data["order_type"],
                            user,
                            data["name"],
                            data["company_email"],
                            data["extras"],
                            data["space"],
                            duration,
                            [],
                            order_cde,
                            order_time,
                            booking_type,
                            data.get("notes", ""),
                            offline_booking,
                        )
                        if "error" in booking:
                            booking_error = booking["error"]
                            break
                    if booking_error:
                        return Response(
                            {"message": booking_error},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    if not offline_booking:
                        return Response(
                            {
                                "message": f"Awaiting payment",
                                "payload": {"order_code": order_cde, "transaction_code":data["transaction_code"]},
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        send_booking_mail(
                            customer_email,
                            space.agent.user.email,
                            data.get("name"),
                            space.agent.user.name,
                            space,
                        )
                        return Response(
                            {
                                "message": f"Booking successful",
                                "payload": {"order_code": order_cde},
                            },
                            status=status.HTTP_200_OK,
                        )

            except IntegrityError as e:
                return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)


class BookingList(APIView):
    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def get(self, request, format=None):
        bookings = Order.objects.filter(order_type__order_type="booking")
        serializer = OrderSerializer(bookings, many=True)

        return Response(
            {"message": "Bookings fetched successfully", "payload": serializer.data},
            status=status.HTTP_200_OK,
        )


class BookingCancellation(APIView):
    permission_classes = [IsAuthenticated]

    def get_agent(self, agent_id):
        try:
            return Agent.objects.get(agent_id=agent_id)
        except Agent.DoesNotExist:
            return False

    def get_customer(self, customer_id):
        try:
            return Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return False

    def post(self, request):
        reason = request.data.get("reason")
        order_id = request.data.get("order_id")
        agent_id = request.data.get("agent_id")
        customer_id = request.data.get("customer_id")
        agent = self.get_agent(agent_id)

        customer = self.get_customer(customer_id)
        if not agent:
            return Response(
                {"message": "Agent not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if not customer:
            return Response(
                {"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND
            )

        all_admin = User.objects.filter(is_super=True)
        admin_email_list = [admin.email for admin in all_admin if all_admin]

        agent_mail = agent.user.email
        customer_mail = customer.user.email
        agent_name = agent.user.name
        customer_name = customer.user.name
        try:
            booking = Order.objects.get(orders_id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"message": f"No order with the given booking id {order_id} found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        booking.status = "cancelation request"
        booking.save()
        cancellation_data = {
            "reason": reason,
            "agent": agent_id,
            "customer": customer_id,
            "booking": f"{booking.orders_id}",
        }
        serializer = CancellationSerializer(data=cancellation_data)

        if serializer.is_valid():
            serializer.save()
            sender = config("EMAIL_SENDER", default="space.ng@gmail.com")

            # notification for customer booking space
            subject_customer = "BOOKING CANCELLATION REQUEST SENT"
            to_customer = customer_mail
            customer_content = f"Dear {customer_name}, your Booking Cancellation request has been sent successfully. The space host would get back to you soon on the status of your request"

            # notification for agent that registered space
            # subject_agent = "YOU HAVE A BOOKING CANCELLATION REQUEST"
            # to_agent = agent_mail
            # agent_content = f"""Dear {agent_name}, Customer {customer_name} has requested cancellation of a booking with code {booking.order_code} and this is the reason
            # {reason}.
            # kindly visit dashboard to accept or decline request """

            guest_template = get_template(
                "api/order/customer_booking_cancellation_request.html"
            )
            guest_content = guest_template.render(
                {
                    "guest_name": customer_name,
                    "login_url": f"{config('FRONTEND_URL')}/signin",
                }
            )
            msg = EmailMultiAlternatives(
                subject_customer, guest_content, sender, to=[to_customer]
            )
            msg.attach_alternative(guest_content, "text/html")
            msg.send()

            admin_template = get_template("api/admin/booking_cancellation_request.html")
            admin_content = admin_template.render(
                {
                    "guest_name": customer_name,
                    "login_url": f"{config('FRONTEND_URL')}/signin",
                }
            )
            msg = EmailMultiAlternatives(
                subject_customer, admin_content, sender, to=[admin_email_list]
            )
            msg.attach_alternative(admin_content, "text/html")
            msg.send()

            subscriber.connect(notification_creator)
            subscriber.send(
                sender=self.__class__,
                data={
                    "user_id": f"{agent.user.user_id}",
                    "notification": f"You have a new booking cancellation request for booking {booking.order_code} ",
                },
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.custom_full_errors, status=status.HTTP_400_BAD_REQUEST
        )


class BookingCancellationActions(APIView):
    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def approve_cancellation(
        self, booking, cancel, agent_email, agent_name, customer_email, customer_name
    ):
        # to approve extension time
        try:
            with transaction.atomic():
                booking.status = "cancelled"
                space_name = booking.space.name
                space_location = booking.space.address
                booking.save()
                cancel.status = "accept"
                cancel.save()
                # notifications
                sender = config("EMAIL_SENDER", default="space.ng@gmail.com")
                # notification for customer booking space
                subject_customer = "REQUEST FOR CANCELLATION APPROVED"
                to_customer = customer_email
                # customer_content = f"Dear {customer_name}, your request for booking cancellation as been approved by the Space Host. Refund would be processed shortly"

                # notification for agent that registered space
                subject_agent = "YOU JUST APPROVED A REQUEST FOR BOOKING CANCELLATION"
                to_agent = agent_email
                # agent_content = f"Dear {agent_name}, You have approved a request for Booking cancellation."

                guest_template = get_template(
                    "api/order/customer_booking_cancellation_approved.html"
                )
                guest_content = guest_template.render(
                    {
                        "guest_name": customer_name,
                        "login_url": f"{config('FRONTEND_URL')}/signin",
                        "space_name": space_name,
                        "space_location": space_location,
                    }
                )
                msg = EmailMultiAlternatives(
                    subject_customer, guest_content, sender, to=[to_customer]
                )
                msg.attach_alternative(guest_content, "text/html")
                msg.send()

                host_template = get_template(
                    "api/order/space_host_booking_cancellation_approved.html"
                )
                host_content = host_template.render(
                    {
                        "host_name": agent_name,
                        "login_url": f"{config('FRONTEND_URL')}/signin",
                        "space_name": space_name,
                        "space_location": space_location,
                    }
                )
                msg = EmailMultiAlternatives(
                    subject_agent, host_content, sender, to=[to_agent]
                )
                msg.attach_alternative(host_content, "text/html")
                msg.send()
                return Response(
                    {"message": "Booking cancellation request success"},
                    status=status.HTTP_200_OK,
                )
        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def decline_cancellation_request(
        self, cancel, reason, agent_email, agent_name, customer_email, customer_name
    ):
        # to approve extension time
        try:
            with transaction.atomic():
                cancel.status = "declined"
                cancel.save()
                space_name = cancel.booking.space.name
                space_location = cancel.booking.space.address
                sender = config("EMAIL_SENDER", default="space.ng@gmail.com")
                # notification for customer booking space
                subject_customer = "REQUEST FOR CANCELLATION DECLINED"
                to_customer = customer_email
                customer_content = f"Dear {customer_name}, your request for booking cancellation as been DECLINED by the Space Host. for the following reason \n {reason}"

                # notification for agent that registered space
                subject_agent = "YOU JUST DECLINED A REQUEST FOR BOOKING CANCELLATION"
                to_agent = agent_email
                agent_content = f"Dear {agent_name}, You have Declined a request for Booking cancellation."

                guest_template = get_template(
                    "api/order/customer_booking_cancellation_denied.html"
                )
                guest_content = guest_template.render(
                    {
                        "guest_name": customer_name,
                        "login_url": f"{config('FRONTEND_URL')}/signin",
                        "space_name": space_name,
                        "space_location": space_location,
                    }
                )
                msg = EmailMultiAlternatives(
                    subject_customer, guest_content, sender, to=[to_customer]
                )
                msg.attach_alternative(guest_content, "text/html")
                msg.send()

                return Response(
                    {"message": "Booking cancellation request declined"},
                    status=status.HTTP_200_OK,
                )
        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, cancellation_id):
        update_type = request.data.get("update_type")

        try:
            cancel = Cancellation.objects.get(cancellation_id=cancellation_id)
        except Cancellation.DoesNotExist:
            return Response(
                {"message": "Cancellation ID not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        customer_email = cancel.customer.user.email
        agent_email = cancel.agent.user.email
        booking_id = cancel.booking.orders_id
        agent_name = cancel.agent.user.name
        customer_name = cancel.customer.user.name
        try:
            booking = Order.objects.get(orders_id=booking_id)
        except Order.DoesNotExist:
            return Response(
                {"message": "No booking for this cancellation request found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if update_type == "accept":
            return self.approve_cancellation(
                booking, cancel, agent_email, agent_name, customer_email, customer_name
            )
        elif update_type == "decline":
            reason = request.data.get("reason")
            return self.decline_cancellation_request(
                cancel, reason, agent_email, agent_name, customer_email, customer_name
            )


class UpdateReferenceCode(APIView):
    def get_orders(self, order_code):
        try:
            return Order.objects.filter(order_code=order_code)
        except Order.DoesNotExist:
            return False

    def put(self, request, order_code):
        orders = self.get_orders(order_code)
        if not orders:
            return Response(
                {"message": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
            )
        transaction_code = request.data.get("reference")
        if not transaction_code:
            return Response(
                {"message": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
            )
        booked = []
        for order_obj in orders:
            order_obj.transaction_code = transaction_code
            booked.append(
                {
                    "start_date": order_obj.usage_start_date,
                    "end_date": order_obj.usage_end_date,
                }
            )
            order_obj.save()

        order = orders.first()
        customer_email = order.user.email
        customer_name = order.name
        space = order.space
        space.number_of_bookings += 1
        space.save()
        customer_details = {
            "id": order.user.user_id,
            "name": customer_name,
            "email": customer_email,
        }
        if order.status == "booked":

            return Response(
                {
                    "payload": {
                        **customer_details,
                        "order_code": order_code,
                        "Booking dates": booked,
                    },
                    "message": f"Booking completed",
                },
                status = status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    "payload": {
                        **customer_details,
                        "order_code": order_code,
                        "Booking dates": booked,
                    },
                    "message": f"Awaiting paystack confirmation",
                },
                status = status.HTTP_200_OK
            )


class PreviousBookingPerUser(APIView):
    def get(self, request, user_id):
        order_type = OrderType.objects.get(order_type="booking")
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        bookings = Order.objects.filter(order_type=order_type, user=user)
        now = datetime.now()
        bookings.filter(usage_end_date__lt=now)

        serializer = OrdersFetchSerializer(bookings, many=True)

        return Response(
            {
                "message": "Previous booking fetched successfully",
                "payload": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UpcomingBookingPerUser(APIView):
    def get(self, request, user_id):
        order_type = OrderType.objects.get(order_type="booking")
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        bookings = Order.objects.filter(order_type=order_type, user=user)
        now = datetime.now()
        bookings.filter(usage_end_date__gt=now)

        serializer = OrdersFetchSerializer(bookings, many=True)

        return Response(
            {
                "message": "Upcoming booking fetched successfully",
                "payload": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class BookingCancellationPerUser(APIView):
    def get(self, request, customer_id):

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND
            )

        cancellation = Cancellation.objects.filter(customer=customer)

        if not cancellation:
            return Response(
                {"message": "No cancellation made"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = CancellationFetchSerializer(cancellation, many=True)

        return Response(
            {
                "message": "Cancellations successfully fetched",
                "payload": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class BookingAnalytics(APIView):
    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def get(self, request, agent_id):
        try:
            agent = Agent.objects.get(agent_id=uuid.UUID(agent_id))
        except:
            return Response(
                {"message": "Agent not found"}, status=status.HTTP_404_NOT_FOUND
            )

        str_start_date = request.GET.get("start_date")
        start_date = datetime.fromisoformat(str_start_date.replace("Z", "+00:00"))

        str_end_date = request.GET.get("end_date")
        end_date = datetime.fromisoformat(str_end_date.replace("Z", "+00:00"))

        bookings_within_range = Order.objects.filter(
            space__agent__agent_id=agent_id,
            order_type__order_type="booking",
            order_time__range=[start_date, end_date],
        )
        no_of_bookings_within_range = len(bookings_within_range)
        return Response(
            {
                "message": f"Bookings between {start_date} and {end_date} were successfully fetched.",
                "number_of_bookings": no_of_bookings_within_range,
            },
            status=status.HTTP_200_OK,
        )
