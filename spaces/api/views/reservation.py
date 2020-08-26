from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, date, timedelta
from decouple import config
from django.core.mail import send_mail
import calendar
import json
import pytz

from ..models.user import User
from ..models.agent import Agent
from ..models.spaces import Space
from ..models.order import Order
from ..models.order_type import OrderType
from ..models.availabilities import Availability
from ..helper.helper import order_code
from ..serializers.order import OrderSerializer
from .order import PlaceOrder
from django.db import transaction, IntegrityError


class Reservation(PlaceOrder):

    def post(self, request):

        if request.user:
            user = getattr(request._request, 'user', None).id
        else:
            user = ''

        data = request.data
        start = datetime.fromisoformat(
            data['usage_start_date'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(
            data['usage_end_date'].replace('Z', '+00:00'))
        start_day = calendar.day_name[start.weekday()]
        end_day = calendar.day_name[end.weekday()]
        end_time = end.hour
        start_time = start.hour
        start_date = start.day
        end_date = end.day
        start_month = start.month
        end_month = end.month
        start_year = start.year
        end_year = end.year

        space_id = data["space"]
        order_type_name = data["order_type"]
        name = data["name"]
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

        now = timezone.now()
        reservation_expiry = now + timedelta(seconds=21600)
        order_cde = order_code()

        if duration == 'hourly':
            hours_booked = json.dumps(data['hours_booked'])
        else:
            hours_booked = ''

        def make_reservation():

            order_data = {
                'amount': amount,
                'usage_start_date': start,
                'usage_end_date': end,
                'status': 'pending',
                'transaction_code': "none",
                'order_code': order_cde,
                'order_type': self.get_order_type_id(order_type_name),
                'no_of_guest': no_of_guest,
                'user': user,
                'name': name,
                'company_email': email,
                'extras': extras,
                'space': space_id,
                'duration': duration,
                'hours_booked': hours_booked,

            }

            order_serializer = OrderSerializer(data=order_data)
            if order_serializer.is_valid():
                order_serializer.save()

                sender = config("EMAIL_SENDER", default="space.ng@gmail.com")

                # notification for customer
                subject_customer = "SPACE RESERVED"
                to_customer = [email]
                customer_content = f"Dear {name}, You reserved space {space.name} for use from {start_date} to {end_date}, your order code is {order_cde}. Kindly proceed to make payment and complete order by supplying your order code upon login before {reservation_expiry}. Thanks for your patronage"

                send_mail(subject_customer, customer_content,
                          sender, to_customer)

                customer_details = {"id": user, "name": name, "email": email}

                return Response(
                    {"payload": {**customer_details, "booking_start_date": start_date, "booking_end_date": end_date, "order_code": order_cde},
                        "message": f"{space.name} reserved from 2020-04-27 to 2020-04-29"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"error": order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        def get_active_orders(start):
            orders = Order.objects.filter(space=space_id)
            active_orders = [
                order for order in orders if order.usage_end_date >= start]
            return active_orders

        def reserve(active_orders, start_date, duration_type):
            if active_orders:
                for order in active_orders:
                    order_end_date = order.usage_end_date
                    order_type = order.order_type.order_type

                    if start_date <= order_end_date:
                        if order_type == "booking":
                            return Response({"message": f"Space unavailable, pick a duration_type later than {active_orders[-1].usage_end_date} or check another space"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                        elif order_type == "reservation":
                            expiry_time = order.order_time + \
                                timedelta(seconds=21600)

                            return Response({"message": f"Recheck space availablity at {expiry_time} or pick another day later than {active_orders[-1].usage_end_date}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                        else:
                            return Response({'message': 'Invalid order type'})
                    else:
                        return make_reservation()
            else:
                return make_reservation()

        active_orders = get_active_orders(start)
        opening_period = self.check_all_day(availability, start_day)

        if duration == 'hourly':
            if self.invalid_time(start_time, end_time):
                if opening_period == True:
                    return reserve(active_orders, start_date, 'time')
                else:
                    opening = [time.strftime("%m-%d-%Y, %H:%M")
                               for time in opening_period]
                    open_time = opening[0]
                    close_time = opening[1]
                    if open_time > start_time:
                        return Response({"message": f"Space opens between {open_time} to {close_time}"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return reserve(active_orders, start)
            else:
                return Response({"message": "Usage end time must be a later than start time"}, status=status.HTTP_400_BAD_REQUEST)

        elif duration == 'daily':
            if self.invalid_time(start_date, end_date):
                return reserve(active_orders, start, date)
            else:
                return Response({"message": "Usage end date must be a later than start date"}, status=status.HTTP_400_BAD_REQUEST)

        elif duration == 'monthly':
            if self.invalid_time(start_month, end_month):
                return reserve(active_orders, start)
            else:
                return Response({"message": "Usage end month must be a later than start month"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            if self.invalid_time(start_year, end_year):
                return reserve(active_orders, start, 'year')
            else:
                return Response({"message": "Usage end year must be a later than start year"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        data = request.data
        user = request.user
        customer = get_object_or_404(User, user_id=user.id)
        order_code = data['order_code']
        transaction_code = data['transaction_code']
        order = get_object_or_404(Order, order_code=order_code)
        space = self.get_space(order.space.space_id)

        # NOTE: create_space endpoint allows the same space to be created more than once, this should be checked!!!
        agent = self.get_agent(space.agent)

        if order.status == "pending":
            if order_code:
                if transaction_code != "none":

                    order.transaction_code = transaction_code
                    order.status = "booked"
                    order.save()

                    sender = config(
                        "EMAIL_SENDER", default="space.ng@gmail.com")
                    subject_agent = "YOU HAVE A RESERVED ORDER"
                    to_agent = [agent.email]
                    agent_content = f"Dear {agent.name}, space {space.name} listed on our platform has been reser from {order.usage_start_date} to {order.usage_end_date}."

                    subject_customer2 = "ORDER COMPLETED"
                    to_customer = [customer.email]
                    customer_content2 = f"Dear {customer.name}, Your order {order_code} for {space.name} has been completed. Thanks for your patronage"

                    send_mail(subject_agent, agent_content, sender, to_agent)
                    send_mail(subject_customer2, customer_content2,
                              sender, to_customer)

                    return Response({"message": "Order completed", "status": f"{order.status}"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Kindly make payment to proceed"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Provide order code to proceed'})
        else:
            return Response({"message": "Reservation has expired, click on booking link to make a fresh booking"}, status=status.HTTP_406_NOT_ACCEPTABLE)


class PlaceReservation(PlaceOrder):

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

    def reserve_space(self, amount, start_date, end_date, transaction_code, no_of_guest, order_type_name, user, name, email, extras, space_id, duration, hours_booked, order_cde, order_time):

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
            if duration == "daily":
                if start_date.date() - pytz.utc.localize((now+timedelta(days=1)).date()) < timedelta(days=1):
                    days_not_allowed.append(book)
            elif duration == "hourly":
                if start_date - pytz.utc.localize((now+timedelta(hours=24))) < timedelta(hours=24):
                    days_not_allowed.append(book)

        return days_not_allowed
    # checks for booked dates

    def booked_days(self, start_date, end_date, space_id, duration):
        orders = Order.objects.filter(
            space=space_id).exclude(status="cancelled")

        if duration == "hourly":
            active_orders = [
                order for order in orders if pytz.utc.localize(order.usage_end_date) >= start_date]
        elif duration == "daily":
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
                if (start >= order_start_date and start_date <= order_end_date) or (end <= order_end_date and end >= order_start_date):
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

        # if request.user:
        #     user = getattr(request._request, 'user', None).id
        # else:
        #     user = ''

        data = request.data
        space_id = data["space"]
        name = data["name"]
        email = data['company_email']
        space = self.get_space(space_id)
        agent = self.get_agent(space.agent)

        agent_name = agent.name
        agent_mail = agent.email

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
                return Response({"message": f"You can only place reservations 24 hours ahead and not on the same day"}, status=status.HTTP_400_BAD_REQUEST)

            
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
            # print({"existing": existing_bookings})
            for hours in hours_booked:
                ordered = self.order(existing_bookings,
                                     hours["start_date"], hours["end_date"], duration)
                exists.extend(ordered)

        elif duration == "daily":
            days_booked = json.loads(json.dumps(data.get("daily_bookings")))
            invalid_time_array = self.invalid_time(days_booked)
            # Gets all existing bookings
            check = self.check_day_difference(days_booked, duration, now)

            if check:
                return Response({"message": f"You can only place reservations 24 hours ahead and not on the same day"}, status=status.HTTP_400_BAD_REQUEST)

            for days in days_booked:
                start_date = datetime.fromisoformat(
                    days["start_date"].replace('Z', '+00:00')).date()
                existing_bookings.extend(self.booked_days(
                    datetime.fromisoformat(days["start_date"].replace('Z', '+00:00')), datetime.fromisoformat(days["end_date"].replace('Z', '+00:00')), space_id, duration))

            for days in days_booked:

                ordered = self.order(existing_bookings,
                                     days["start_date"], days["end_date"], duration)
                exists.extend(ordered)

            # if not invalid_time_array:

            # pass
        if (bool(exists)):
            if duration == "daily":
                return Response({"message": f"Space is not available on the following days", "payload": days_booked}, status=status.HTTP_409_CONFLICT)
            elif duration == "hourly":
                return Response({"message": f"Space is not available on the following hours", "payload": hours}, status=status.HTTP_409_CONFLICT)
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
                    if duration == "daily":
                        booked = days_booked
                    elif duration == "hourly":
                        booked = hours_booked

                    for days in booked:
                        start = datetime.fromisoformat(
                            days['start_date'].replace('Z', '+00:00'))
                        end = datetime.fromisoformat(
                            days['end_date'].replace('Z', '+00:00'))

                        self.reserve_space(data["amount"], start, end, data["transaction_code"], data["no_of_guest"], data["order_type"],
                                           user, data["name"], data["company_email"], data["extras"], data["space"], duration, [], order_cde, order_time)
                    # notifications
                    sender = config(
                        "EMAIL_SENDER", default="space.ng@gmail.com")
                    next_day = order_time + timedelta(days=1)
                    # notification for customer booking space
                    subject_customer = "RESERVATION COMPLETE"
                    to_customer = [customer_email]
                    customer_content = f"Dear {data['email']}, your Reservation has been completed. You reserved space is {space.name} and would expire by {next_day.time()} {next_day.date()}. Thanks for your patronage."

                    # notification for agent that registered space
                    subject_agent = "YOU HAVE A RESERVATION"
                    to_agent = [agent_mail]
                    agent_content = f"Dear {agent_name}, you have a reservation placed for your space {space.name} listed on our platform. accept the reservation now. Or it would expire by {next_day.time()} {next_day.date()}. "

                    send_mail(subject_agent, agent_content,
                              sender, to_agent)
                    send_mail(subject_customer, customer_content,
                              sender, to_customer)

                    customer_details = {
                        "id": user, "name": name, "email": email}

                    return Response(
                        {"payload": {**customer_details, "order_code": order_cde, "Reservation dates": booked},
                            "message": f"Reservation completed"},
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
                # notifications
                sender = config(
                    "EMAIL_SENDER", default="space.ng@gmail.com")
                next_day = start_now + timedelta(days=1)
                # notification for customer booking space
                subject_customer = "RESERVATION APPROVED"
                to_customer = [customer.email]
                customer_content = f"Dear {customer.name}, your Reservation has been Accepted by the space host. You reserved space is {space.name} and would expire by {next_day.time()} {next_day.date()} Remember you can request for extension before it expires. Thanks for your patronage"

                # notification for agent that registered space
                subject_agent = "YOU JUST APPROVED A RESERVATION"
                to_agent = [agent_mail]
                agent_content = f"Dear {agent_name}, You have approved a reservation for {space.name} listed on our platform. It would expire by {next_day.time()} {next_day.date()}. This expiry is subject to request for extension by the customer "

                send_mail(subject_agent, agent_content,
                          sender, to_agent)
                send_mail(subject_customer, customer_content,
                          sender, to_customer)
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
                # notifications
                sender = config(
                    "EMAIL_SENDER", default="space.ng@gmail.com")
                # notification for customer booking space
                subject_customer = "RESERVATION CANCELLED"
                to_customer = [customer.email]
                customer_content = f"Dear {customer.name}, your Reservation has been Declined by the space host. Kindly book for the space or choose another space for reservation. Thanks for your patronage"

                # notification for agent that registered space
                subject_agent = "YOU JUST DECLINED A RESERVATION"
                to_agent = [agent_mail]
                agent_content = f"Dear {agent_name}, You have declined a reservation for {space.name} listed on our platform."

                send_mail(subject_agent, agent_content,
                          sender, to_agent)
                send_mail(subject_customer, customer_content,
                          sender, to_customer)
        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)    
    
    def approve_reservation_extension(self, orders, data, agent_mail, space, transaction_code, customer):
        #to approve extension time
        try:
            with transaction.atomic():
                start_now = datetime.now()
                for order in orders:
                    if order.status == "pending":
                        order.status = "reserved"
                        order.expiry_time = start_now + timedelta(days=1)
                        order.save()
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

                send_mail(subject_agent, agent_content,
                          sender, to_agent)
                send_mail(subject_customer, customer_content,
                          sender, to_customer)
        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def reservation_to_booking(self, orders, data, agent_mail, agent_name, space, transaction_code, customer):
        try:
            with transaction.atomic():
                start_now = datetime.now()
                for order in orders:
                    if order.status == "pending":
                        order.status = "booked"
                        order.order_time = start_now
                        order.transaction_code = transaction_code
                        order.save()
                # notifications
                sender = config(
                    "EMAIL_SENDER", default="space.ng@gmail.com")
                subject_agent = "A RESERVED SPACE HAS JUST BEEN BOOKED"
                to_agent = [agent_mail]
                agent_content = f"Dear {agent_name}, space {space.name} listed on our platform has been booked."

                subject_customer2 = "ORDER COMPLETED"
                to_customer = [customer.email]
                customer_content2 = f"Dear {customer.name}, Your order {order_code} for {space.name} has been completed. Thanks for your patronage"

                send_mail(subject_agent, agent_content, sender, to_agent)
                send_mail(subject_customer2, customer_content2,
                          sender, to_customer)

                return Response({"message": "Order completed", "status": f"{order.status}"}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        data = request.data
        user_id = data["user"]
        update_type = data["update_type"]
        customer = get_object_or_404(User, user_id=user_id)
        order_code = data['order_code']
        transaction_code = data['transaction_code']
        try:
            orders = Order.objects.filter(order_code=order_code)
        except:
            return Response({"message": "orders with order code {order_code} not found"}, status=status.HTTP_404_NOT_FOUND)
        space = self.get_space(list(orders)[0].space.space_id)

        # NOTE: create_space endpoint allows the same space to be created more than once, this should be checked!!!
        agent = self.get_agent(space.agent)
        agent_mail = agent.email
        agent_name = agent.name
        
        if order_code:
            if update_type == "book":
                    self.reservation_to_booking(
                        orders, data, agent_mail, agent_name, space, transaction_code, customer)
            elif update_type == "approve" or update_type == "decline":
                if request.user.is_authenticated:
                    if update_type == "approve":
                            self.approve_reservation(
                                orders, data, agent_mail, agent_name, space, customer)
                    elif update_type == "decline":
                        self.decline_reservation(
                            orders, data, agent_mail, agent_name, space, customer)                    
                else:
                    return Response({"message": "Login as a space host to complete this action."})
            else:
                return Response({"message": "Invalid update type"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Order code not provided"}, status=status.HTTP_400_BAD_REQUEST)


class RequestReservationExtension(APIView):
    def post(self, request):
        data = request.data
        user_id = data["user"]
        reason = data["reason"]
        customer = get_object_or_404(User, user_id=user_id)
        order_code = data['order_code']
        try:
            orders = Order.objects.filter(order_code=order_code)
        except:
            return Response({"message": "orders with order code {order_code} not found"}, status=status.HTTP_404_NOT_FOUND)
        space = self.get_space(list(orders)[0].space.space_id)
        agent = self.get_agent(space.agent)
        agent_mail = agent.email
        agent_name = agent.name
        # transaction_code = data['transaction_code']
        
        try:
            # notifications
            sender = config(
                "EMAIL_SENDER", default="space.ng@gmail.com")
        
            subject_customer = "REQUEST FOR RESERVATION EXTENSION"
            to_customer = [customer.email]
            customer_content = f"Dear {customer.name}, you have requested for an extension of time on your reservation. You reserved space is {space.name}. Your request awaits approval of the space host, you will be notified once this is done. Thanks for your patronage."

            # notification for agent that registered space
            subject_agent = "YOU HAVE A REQUEST FOR RESERVATION EXTENSION"
            to_agent = [agent_mail]
            agent_content = f"Dear {agent_name}, {customer.name} has requested for extension of reservation time for the reason stated below;\n {reason}.\n Approve the extension time or it expires at the previously slated time."

            send_mail(subject_agent, agent_content,
                        sender, to_agent)
            send_mail(subject_customer, customer_content,
                        sender, to_customer)
        except :
            return Response({"error": "invalid"}, status=status.HTTP_400_BAD_REQUEST)