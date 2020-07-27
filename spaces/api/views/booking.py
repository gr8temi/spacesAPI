from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from datetime import date, timedelta, datetime
from rest_framework.permissions import IsAuthenticated
from decouple import config
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json
import calendar
import time
from ..models.spaces import Space
from ..models.order import Order
from ..models.agent import Agent
from ..models.user import User
from ..models.order_type import OrderType
from ..helper.helper import order_code
from ..serializers.order import OrderSerializer
from ..serializers.user import UserSerializer
from .order import PlaceOrder
from ..models.availabilities import Availability
import pytz
from django.db import transaction, IntegrityError


class Booking(PlaceOrder):

    def post(self, request):

        data = request.data

        start = datetime.fromisoformat(
            data['usage_start_date'].replace('Z', '+00:00'))

        end = datetime.fromisoformat(
            data['usage_end_date'].replace('Z', '+00:00'))
        # end = datetime.fromisoformat(
        #     data['usage_end_date'].replace('Z', '+00:00'))
        start_day = calendar.day_name[start.weekday()]
        end_day = calendar.day_name[end.weekday()]
        end_time = end.time()
        start_time = start.time()
        start_date = start.date()
        end_date = end.date()
        start_month = start.month
        end_month = end.month
        start_year = start.year
        end_year = end.year

        space_id = data["space"]
        order_type_name = data["order_type"]
        name = data['name']
        email = data['company_email']
        extras = json.dumps(data['extras'])
        amount = data['amount']
        no_of_guest = data['no_of_guest']

        space = self.get_space(space_id)
        agent = self.get_agent(space.agent)

        agent_name = agent.name
        agent_mail = agent.email

        today = timezone.now().date()
        duration = space.duration

        space_availability = Availability.objects.filter(space=space.name)

        availability = [{'day': av.day, 'all_day': av.all_day, 'open_time': av.open_time,
                         'close_time': av.close_time} for av in space_availability]
        if data["user"]:
            user = User.objects.get(user_id=data["user"]).user_id
        else:
            user = ''

        if duration == 'hourly':
            hours_booked = json.dumps(data['hours_booked'])
        else:
            hours_booked = []

        def book_space():

            order_cde = order_code()
            order_data = {
                'amount': amount,
                'usage_start_date': start,
                'usage_end_date': end,
                'status': 'booked',
                'transaction_code': data['transaction_code'],
                'no_of_guest': no_of_guest,
                'order_code': order_cde,
                'order_type': self.get_order_type_id(order_type_name),
                'user': user,
                'name': name,
                'company_email': email,
                'extras': extras,
                'space': space_id,
                'duration': duration,
                'hours_booked': hours_booked
            }

            order_serializer = OrderSerializer(data=order_data)
            if order_serializer.is_valid():
                order_serializer.save()
                # notifications
                sender = config("EMAIL_SENDER", default="space.ng@gmail.com")

                # notification for customer booking space
                subject_customer = "ORDER COMPLETED"
                to_customer = [email]
                customer_content = f"Dear {name}, your Order has been completed. You booked space {space.name} from {start_date} to {end_date}. Thanks for your patronage"

                # notification for agent that registered space
                subject_agent = "YOU HAVE AN ORDER"
                to_agent = [agent_mail]
                agent_content = f"Dear {agent_name}, you have an order placed for your space {space.name} listed on our platform from {start_date} to {end_date}."

                send_mail(subject_agent, agent_content, sender, to_agent)
                send_mail(subject_customer, customer_content,
                          sender, to_customer)

                customer_details = {
                    "id": user, "name": name, "email": email}

                return Response(
                    {"payload": {**customer_details, "order_code": order_cde, "Booking start date": start, "Booking end date": end},
                        "message": f"Order completed"},
                    status=status.HTTP_200_OK)
            return Response({"error": order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        def get_active_orders(start, hours_booked, duration):

            orders = Order.objects.filter(space=space_id)
            active_orders = [
                order for order in orders if pytz.utc.localize(order.usage_end_date) >= start]

            if duration == "hourly":
                active_orders = list(active_orders)

                new_list = []
                for orders in active_orders:
                    if len(orders.hours_booked) > 0:
                        new_list = new_list+json.loads(orders.hours_booked)

                hours_booked = json.loads(hours_booked)
                hours_booked_set = set(
                    (lis["time_in"], lis["time_out"], lis["date"]) for lis in hours_booked)
                new_list_set = set((lis["time_in"], lis["time_out"], lis["date"])
                                   for lis in new_list)

                intersect = hours_booked_set.intersection(new_list_set)

                return intersect
            else:
                return active_orders

        all_day = self.check_all_day(availability, start_day)

        def order(active_order, start, duration):
            if(duration == "hourly" and len(active_order) > 0):
                return Response({"message": f"Space unavailable, pick a later date"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            if len(active_order) > 0:
                for order in active_order:
                    order_end_date = pytz.utc.localize(order.usage_end_date)
                    order_type = order.order_type.order_type
                    if start <= order_end_date:
                        if order_type == "booking":
                            return Response({"message": f"Space unavailable, pick a date later than {order_end_date} or check another space"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                        elif order_type == "reservation":
                            expiry_time = order.order_time + \
                                timedelta(seconds=21600)

                            return Response({"message": f"Recheck space availablity at {expiry_time} or pick another day later than {order_end_date}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                        else:
                            return Response({"message": "Invalid order type"})
                    else:
                        return book_space()
            else:
                return book_space()

        if duration == 'hourly':

            active_orders = get_active_orders(start, hours_booked, "hourly")

            if self.invalid_time(start_time, end_time):
                if all_day == True:
                    return order(active_orders, start_date, "hourly")
                else:
                    #
                    new_start_time = datetime.combine(date.today(), start_time)
                    opening = [datetime.strptime(times.strftime("%H:%M"), "%H:%M")
                               for times in all_day]

                    open_time = opening[0]
                    close_time = opening[1]
                    if open_time > new_start_time:
                        return Response({"message": f"Space opens between {open_time} to {close_time}"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return order(active_orders, start, duration)
            else:
                return Response({"message": "Usage end time must be a later  than start time"}, status=status.HTTP_400_BAD_REQUEST)
        elif duration == 'daily':
            active_orders = get_active_orders(start, [], "daily")
            if self.invalid_time(start_date, end_date):

                return order(active_orders, start, "daily")
            else:
                return Response({"message": "Usage end date must be a later than start date"}, status=status.HTTP_400_BAD_REQUEST)

        elif duration == 'monthly':
            active_orders = get_active_orders(start, [], "monthly")
            if self.invalid_time(start_month, end_month):
                return order(active_orders, start, "monthly")
            else:
                return Response({"message": "Usage end month must be a later than start month"}, status=status.HTTP_400_BAD_REQUEST)

        # else:
        #     if self.invalid_time(start_year, end_year):
        #         return order(active_orders, start, "yearly")
        else:
            return Response({"message": "Usage end year must be a later than start date"}, status=status.HTTP_400_BAD_REQUEST)


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
            elif str(order_type) == "reservation":
                expiry_time = order.order_time + timedelta(seconds=21600)
                return Response({"message": "Reservation fetched successfully", "payload": serializer.data, "expiration": expiry_time}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


class BookingView(PlaceOrder):

    def book_space(self, amount, start_date, end_date, transaction_code, no_of_guest, order_type_name, user, name, email, extras, space_id, duration, hours_booked, order_cde):

        order_data = {
            'amount': amount,
            'usage_start_date': start_date,
            'usage_end_date': end_date,
            'status': 'booked',
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
            'hours_booked': hours_booked
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

    def booked_days(self, start_date, end_date, space_id, duration):
        orders = Order.objects.filter(space=space_id)

        if duration == "hourly":
            active_orders = [
                order for order in orders if order.usage_end_date.time() >= start_date.time()]
            print({"active": active_orders})
        elif duration == "daily":
            active_orders = [
                order for order in orders if pytz.utc.localize(order.usage_end_date).date() >= start_date.date()]
        return active_orders

    def order(self, active_order, start_date, duration):

        start_date = datetime.fromisoformat(
            start_date.replace('Z', '+00:00'))
        # if(duration == "hourly" and len(active_order) > 0):
        #     return Response({"message": f"Space unavailable, pick a later date"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        existing = []
        if len(active_order) > 0:

            for order in active_order:
                if duration == "daily":
                    order_end_date = pytz.utc.localize(order.usage_end_date).date()
                    start = start_date.date()
                elif duration == "hourly":
                    order_end_date = order.usage_end_date.time()
                    
                    start = start_date.time()

                order_type = order.order_type.order_type
                if start <= order_end_date:
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
        space_id = data["space"]
        space = self.get_space(space_id)
        agent = self.get_agent(space.agent)
        orders = Order.objects.all()
        order_array = []
        for order in orders:
            order_array.append(
                {"usage_start_date": order.usage_start_date, "usage_end_date": order.usage_end_date})
        duration = data["duration"]
        name = data['name']
        email = data['company_email']
        days_booked = json.loads(json.dumps(data.get("daily_bookings")))

        hours_booked = json.loads(json.dumps(data.get("hours_booked")))
        agent_name = agent.name
        agent_mail = agent.email
        existing_bookings = []
        false_date = []
        if data["duration"] == "hourly":

            for hours in hours_booked:
                start_date = datetime.fromisoformat(
                    hours["start_date"].replace('Z', '+00:00'))
                if (start_date.date() >= datetime.now().date()):
                    existing_bookings.extend(self.booked_days(
                        datetime.fromisoformat(hours["start_date"].replace('Z', '+00:00')), datetime.fromisoformat(hours["end_date"].replace('Z', '+00:00')), space_id, duration))
                else:
                    false_date.append(True)

        elif data["duration"] == "daily":

            # Gets all existing bookings

            for days in days_booked:
                start_date = datetime.fromisoformat(
                    days["start_date"].replace('Z', '+00:00')).date()
                if (start_date >= datetime.now().date()):
                    existing_bookings.extend(self.booked_days(
                        datetime.fromisoformat(days["start_date"].replace('Z', '+00:00')), datetime.fromisoformat(days["end_date"].replace('Z', '+00:00')), space_id, duration))
                else:
                    false_date.append(True)

        # Get formatted existing bookings
        exists = []

        if (not bool(false_date)):
            if data["duration"] == "daily":

                for days in days_booked:

                    ordered = self.order(existing_bookings,
                                         days["start_date"], data["duration"])
                    exists.extend(ordered)

            elif data["duration"] == "hourly":
                for hours in hours_booked:
                    ordered = self.order(existing_bookings,
                                         hours["start_date"], data["duration"])
                    exists.extend(ordered)

            if (bool(exists)):
                if data["duration"] == "daily":
                    return Response({"message": f"Space is not available on the following days", "payload": days_booked}, status=status.HTTP_409_CONFLICT)
                elif data["duration"] == "hourly":
                    return Response({"message": f"Space is not available on the following days", "payload": hours}, status=status.HTTP_409_CONFLICT)
            else:
                if data["user"]:
                    user = User.objects.get(user_id=data["user"]).user_id
                else:
                    user = ''
                try:
                    with transaction.atomic():
                        order_cde = order_code()
                        if data["duration"] == "daily":
                            booked = days_booked
                        elif data["duration"] == "hourly":
                            booked = hours_booked

                        for days in booked:
                            start = datetime.fromisoformat(
                                days['start_date'].replace('Z', '+00:00'))
                            end = datetime.fromisoformat(
                                days['end_date'].replace('Z', '+00:00'))

                            self.book_space(data["amount"], start, end, data["transaction_code"], data["no_of_guest"], data["order_type"],
                                            user, data["name"], data["company_email"], data["extras"], data["space"], data["duration"], [], order_cde)
                        # notifications
                        sender = config(
                            "EMAIL_SENDER", default="space.ng@gmail.com")

                        # notification for customer booking space
                        subject_customer = "ORDER COMPLETED"
                        to_customer = [data["email"]]
                        customer_content = f"Dear {data['email']}, your Order has been completed. You booked space {space.name}. Thanks for your patronage"

                        # notification for agent that registered space
                        subject_agent = "YOU HAVE AN ORDER"
                        to_agent = [agent_mail]
                        agent_content = f"Dear {agent_name}, you have an order placed for your space {space.name} listed on our platform."

                        send_mail(subject_agent, agent_content,
                                  sender, to_agent)
                        send_mail(subject_customer, customer_content,
                                  sender, to_customer)

                        customer_details = {
                            "id": user, "name": name, "email": email}

                        return Response(
                            {"payload": {**customer_details, "order_code": order_cde, "Booking start date": start, "Booking end date": end},
                                "message": f"Order completed"},
                            status=status.HTTP_200_OK)

                except IntegrityError as e:
                    return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "The date chosen is before today "}, status=status.HTTP_400_BAD_REQUEST)
    #     pass

    # pass
