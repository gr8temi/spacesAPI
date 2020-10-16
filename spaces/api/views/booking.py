import json
import pytz
import calendar
import time
from datetime import date, timedelta, datetime
from decouple import config

from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.core.mail import send_mail

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
from ..serializers.cancelation import CancellationSerializer

from ..consumers.channel_layers import notification_creator
from ..signals import subscriber

from ..permissions.is_agent_permission import UserIsAnAgent
from .order import PlaceOrder


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
                return Response({"message": "Booking fetched successfully", "payload": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


class BookingView(PlaceOrder):
    def invalid_time(self, date_array):
        invalid_dates = []
        for dates in date_array:
            if datetime.fromisoformat(
                dates["start_date"].replace('Z', '+00:00')) > datetime.fromisoformat(
                    dates["end_date"].replace('Z', '+00:00')):
                invalid_dates.append(dates)
        if invalid_dates:
            return invalid_dates
        else:
            return False

    def book_space(self, amount, start_date, end_date, transaction_code, no_of_guest, order_type_name, user, name, email, extras, space_id, duration, hours_booked, order_cde, order_time, booking_type):
        order_data = {
            'amount': amount,
            'usage_start_date': start_date,
            'usage_end_date': end_date,
            'status': 'pending',
            'transaction_code': transaction_code,
            'no_of_guest': no_of_guest,
            'order_code': order_cde,
            'order_type': f"{booking_type}",
            'user': user,
            'name': name,
            'company_email': email,
            'extras': extras,
            'space': space_id,
            'duration': duration,
            'hours_booked': hours_booked,
            'order_time': order_time,
        }

        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order_serializer.save()

            customer_details = {
                "id": user, "name": name, "email": email}

            return {"payload": {**customer_details, "order_code": order_cde, "Booking start date": start_date, "Booking end date": end_date},
                    "message": f"Order completed", status: True}
        else:
            return {"error": order_serializer.errors, status: False}

    def get_active_orders(self, start, space_id):
        orders = Order.objects.filter(space=space_id)
        active_orders = [
            order for order in orders if order.usage_end_date >= start]
        return active_orders

    def check_availability(self, dates_array, model, space, duration):
        space_availability = model.objects.filter(space=space.name)
        availability = [{'day': av.day, 'all_day': av.all_day, 'open_time': av.open_time,
                         'close_time': av.close_time} for av in space_availability]
        if duration == "hourly":
            opened = []
            for dates in dates_array:
                start_day = calendar.day_name[datetime.fromisoformat(
                    dates["start_date"].replace('Z', '+00:00')).weekday()]
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
                            days["dates"]["start_date"].replace('Z', '+00:00')).hour or close_time < datetime.fromisoformat(
                            days["dates"]["end_date"].replace('Z', '+00:00')).hour:
                        not_available_dates.append(
                            {"dates": days["dates"], "open_time": open_time, "close_time": close_time})
                elif days["opening"] == "not_opened":
                    start_day = datetime.fromisoformat(
                        days["dates"]["start_date"].replace('Z', '+00:00'))
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
                book["start_date"].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(
                book["end_date"].replace('Z', '+00:00'))
            if duration == "hourly":
                if start_date - pytz.utc.localize((now+timedelta(hours=24))) < timedelta(hours=24):
                    days_not_allowed.append(book)
            elif duration == "daily":
                if start_date.date() - pytz.utc.localize((now+timedelta(days=1))).date() < timedelta(days=1):
                    days_not_allowed.append(book)
            elif duration == "monthly":
                if (end_date.date() - start_date.date()).days < 28 or (end_date.date() - start_date.date()).days > 31:
                    return Response({"message": "The time different in your booking is not up to a monthly difference"}, status=status.HTTP_400_BAD_REQUEST)
                if start_date.date() - pytz.utc.localize((now+timedelta(days=1))).date() < timedelta(days=1):
                    days_not_allowed.append(book)

        return days_not_allowed

    # def repeated_booking_dates(self, bookings): continue from here
    #     if duration == "daily" or duration == "monthly":

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
            start_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(
            end_date.replace('Z', '+00:00'))

        existing = []
        if len(active_order) > 0:

            for order in active_order:

                if duration == "daily" or duration == "monthly":
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
                    elif order_type == "booking":
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
        space_id = data["space"]
        name = data["name"]
        email = data['company_email']
        # space = self.get_space(space_id)
        # agent = self.get_agent(space.agent.business_name)
        space = Space.objects.get(space_id=space_id)
        agent = Agent.objects.get(business_name=space.agent.business_name)

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
                return Response({"message": f"You can only place bookings 24 hours ahead and not on the same day"}, status=status.HTTP_400_BAD_REQUEST)

            if not check_available_array:
                for hours in hours_booked:
                    start_date = datetime.fromisoformat(
                        hours["start_date"].replace('Z', '+00:00'))
                    existing_bookings.extend(self.booked_days(
                        start_date, datetime.fromisoformat(hours["end_date"].replace('Z', '+00:00')), space_id, duration))
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
                if duration == "daily" or duration == "hourly":
                    return Response({"message": f"You can only place bookings 24 hours ahead and not on the same day"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": f"You can only place bookings 24 hours ahead and not on the same day and bookings must be in monthly intervals"}, status=status.HTTP_400_BAD_REQUEST)

            for days in days_booked:
                start_date = datetime.fromisoformat(
                    days["start_date"].replace('Z', '+00:00')).date()
                existing_bookings.extend(self.booked_days(
                    datetime.fromisoformat(days["start_date"].replace('Z', '+00:00')), datetime.fromisoformat(days["end_date"].replace('Z', '+00:00')), space_id, duration))

            for days in days_booked:

                ordered = self.order(existing_bookings,
                                     days["start_date"], days["end_date"], duration)
                exists.extend(ordered)

        if (bool(exists)):
            if duration == "daily":
                return Response({"message": f"Space is not available on the following days", "payload": days_booked}, status=status.HTTP_409_CONFLICT)
            elif duration == "hourly":
                return Response({"message": f"Space is not available on the following hours", "payload": hours}, status=status.HTTP_409_CONFLICT)
            elif duration == "monthly":
                return Response({"message": f"Space is not available on the following month", "payload": days_booked}, status=status.HTTP_409_CONFLICT)
        else:
            if data["user"]:
                user = User.objects.get(user_id=data["user"]).user_id
                customer_email = User.objects.get(user_id=data["user"]).email
            else:
                user = ''
            try:
                with transaction.atomic():
                    order_cde = order_code()
                    order_time = datetime.now()
                    if duration == "daily" or duration == "monthly":
                        booked = days_booked
                    elif duration == "hourly":
                        booked = hours_booked
                    booking_type = self.get_order_type_id(data["order_type"])
                    for days in booked:
                        start = datetime.fromisoformat(
                            days['start_date'].replace('Z', '+00:00'))
                        end = datetime.fromisoformat(
                            days['end_date'].replace('Z', '+00:00'))

                        self.book_space(data["amount"], start, end, data["transaction_code"], data["no_of_guest"], data["order_type"],
                                        user, data["name"], data["company_email"], data["extras"], data["space"], duration, [], order_cde, order_time, booking_type)
                    return Response({"message": f"Awaiting payment", "payload": {"order_code": order_cde}}, status=status.HTTP_200_OK)

            except IntegrityError as e:
                return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)


class BookingList(APIView):
    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def get(self, request, format=None):
        bookings = Order.objects.filter(order_type__order_type="booking")
        serializer = OrderSerializer(bookings, many=True)

        return Response({"message": "Bookings fetched successfully", "payload": serializer.data}, status=status.HTTP_200_OK)


class BookingCancellation(APIView):
    permission_classes = [IsAuthenticated]

    def get_agent(self, agent_id):
        try:
            return Agent.objects.get(agent_id=agent_id)
        except Agent.DoesNotExist:
            return Response({"message": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)

    def get_customer(self, customer_id):
        try:
            return Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        reason = request.data["reason"]
        booking_code = request.data["booking_code"]
        agent_id = request.data["agent_id"]
        customer_id = request.data["customer_id"]
        agent = self.get_agent(agent_id)
        customer = self.get_customer(customer_id)
        agent_mail = agent.user.email
        customer_mail = customer.user.email
        agent_name = agent.user.name
        customer_name = customer.user.name
        booking = Order.objects.filter(order_code=booking_code).first()
        if not booking:
            return Response({"message": f"booking with code {booking_code} not found"}, status=status.HTTP_404_NOT_FOUND)
        cancellation_data = {
            "reason": reason,
            "agent": agent_id,
            "customer": customer_id,
            "booking": f"{booking.orders_id}"
        }
        serializer = CancellationSerializer(data=cancellation_data)

        if serializer.is_valid():
            serializer.save()
            sender = config(
                "EMAIL_SENDER", default="space.ng@gmail.com")

            # notification for customer booking space
            subject_customer = "BOOKING CANCELLATION REQUEST SENT"
            to_customer = [customer_mail]
            customer_content = f"Dear {customer_name}, your Booking Cancellation request has been sent successfully. The space host would get back to you soon on the status of your request"

            # notification for agent that registered space
            subject_agent = "YOU HAVE A BOOKING CANCELLATION REQUEST"
            to_agent = [agent_mail]
            agent_content = f"""Dear {agent_name}, Customer {customer_name} has requested cancellation of booking with code {booking_code} and this is the reason
            {reason}.
            kindly visit dashboard to accept or decline request """

            send_mail(subject_agent, agent_content,
                      sender, to_agent)
            send_mail(subject_customer, customer_content,
                      sender, to_customer)
            subscriber.connect(notification_creator)
            subscriber.send(sender=self.__class__,
                            data={"user_id": f"{agent.user.user_id}", "notification": f"You have a new booking cancellation request for booking {booking_code} "})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingCancellationActions(APIView):
    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def approve_cancellation(self, bookings, agent_email, agent_name, customer_email, customer_name):
        # to approve extension time
        try:
            with transaction.atomic():
                for booking in bookings:
                    booking.status = "cancelled"
                    booking.save()
                # notifications
                sender = config(
                    "EMAIL_SENDER", default="space.ng@gmail.com")
                # notification for customer booking space
                subject_customer = "REQUEST FOR CANCELLATION APPROVED"
                to_customer = [customer_email]
                customer_content = f"Dear {customer_name}, your request for booking cancellation as been approved by the Space Host. Refund would be processed shortly"

                # notification for agent that registered space
                subject_agent = "YOU JUST APPROVED A REQUEST FOR BOOKING CANCELLATION"
                to_agent = [agent_email]
                agent_content = f"Dear {agent_name}, You have approved a request for Booking cancellation."

                send_mail(subject_agent, agent_content,
                          sender, to_agent)
                send_mail(subject_customer, customer_content,
                          sender, to_customer)
                return Response({"message": "Booking cancellation request success"}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def decline_cancellation_request(self, reason, agent_email, agent_name, customer_email, customer_name):
        # to approve extension time
        try:
            with transaction.atomic():
                sender = config(
                    "EMAIL_SENDER", default="space.ng@gmail.com")
                # notification for customer booking space
                subject_customer = "REQUEST FOR CANCELLATION DECLINED"
                to_customer = [customer_email]
                customer_content = f"Dear {customer_name}, your request for booking cancellation as been DECLINED by the Space Host. for the following reason \n {reason}"

                # notification for agent that registered space
                subject_agent = "YOU JUST DECLINED A REQUEST FOR BOOKING CANCELLATION"
                to_agent = [agent_email]
                agent_content = f"Dear {agent_name}, You have Declined a request for Booking cancellation."

                send_mail(subject_agent, agent_content,
                          sender, to_agent)
                send_mail(subject_customer, customer_content,
                          sender, to_customer)
                return Response({"message": "Booking cancellation request declined"}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, cancellation_id):
        update_type = request.data["update_type"]

        try:
            cancel = Cancellation.objects.get(cancellation_id=cancellation_id)
        except Cancellation.DoesNotExist:
            return Response({"message": "Cancellation ID not found"}, status=status.HTTP_404_NOT_FOUND)

        customer_email = cancel.customer.user.email
        agent_email = cancel.agent.user.email
        booking_code = cancel.booking.order_code
        agent_name = cancel.agent.user.name
        customer_name = cancel.customer.user.name

        bookings = Order.objects.filter(order_code=booking_code)
        if update_type == "accept":
            return self.approve_cancellation(bookings, agent_email, agent_name, customer_email, customer_name)
        elif update_type == "decline":
            reason = request.data["reason"]
            return self.decline_cancellation_request(
                reason, agent_email, agent_name, customer_email, customer_name)


class UpdateReferenceCode(APIView):
    def get_orders(self, order_code):
        try:
            return Order.objects.filter(order_code=order_code)
        except Order.DoesNotExist:
            return False

    def put(self, request, order_code):
        orders = self.get_orders(order_code)
        if not orders:
            return Response({"message": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        transaction_code = request.data["reference"]
        if not transaction_code:
            return Response({"message": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        booked = []
        for order_obj in orders:
            order_obj.transaction_code = transaction_code
            booked.append({"start_date": order_obj.usage_start_date,
                           "end_date": order_obj.usage_end_date})
            order_obj.save()

        order = orders.first()
        customer_email = order.user.email
        agent = order.space.agent
        agent_mail = agent.user.email
        agent_name = agent.user.name
        customer_name = order.name
        space = order.space

        # notifications
        sender = config(
            "EMAIL_SENDER", default="space.ng@gmail.com")

        # notification for customer booking space
        subject_customer = "BOOKING COMPLETE"
        to_customer = [customer_email]
        customer_content = f"Dear {to_customer}, your Booking has been completed"

        # notification for agent that registered space
        subject_agent = "YOU HAVE A BOOKING"
        to_agent = [agent_mail]
        agent_content = f"Dear {agent_name}, you have a booking placed for your space {space.name} listed on our platform."

        send_mail(subject_agent, agent_content,
                  sender, to_agent)
        send_mail(subject_customer, customer_content,
                  sender, to_customer)

        subscriber.connect(notification_creator)
        subscriber.send(sender=self.__class__,
                        data={"user_id": f"{agent.user.user_id}", "notification": f"You have a new booking {order_code} "})
        customer_details = {
            "id": order.user.user_id, "name": customer_name, "email": customer_email}

        return Response(
            {"payload": {**customer_details, "order_code": order_code, "Booking dates": booked},
             "message": f"Booking completed"},)


class PreviousBookingPerUser(APIView):

    def get(self, request, user_id):
        order_type = OrderType.objects.get(order_type="booking")
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        bookings = Order.objects.filter(order_type=order_type, user=user)
        now = datetime.now()
        bookings.filter(usage_end_date__lt=now)

        serializer = OrdersFetchSerializer(bookings, many=True)

        return Response({"message": "Previous booking fetched successfully", "payload": serializer.data}, status=status.HTTP_200_OK)


class UpcomingBookingPerUser(APIView):

    def get(self, request, user_id):
        order_type = OrderType.objects.get(order_type="booking")
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        bookings = Order.objects.filter(order_type=order_type, user=user)
        now = datetime.now()
        bookings.filter(usage_end_date__gt=now)

        serializer = OrdersFetchSerializer(bookings, many=True)

        return Response({"message": "Upcoming booking fetched successfully", "payload": serializer.data}, status=status.HTTP_200_OK)
