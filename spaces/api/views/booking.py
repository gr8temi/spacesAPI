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

from ..models.spaces import Space
from ..models.order import Order
from ..models.agent import Agent
from ..models.user import User
from ..models.order_type import OrderType
from ..helper.helper import order_code
from ..serializers.order import OrderSerializer
from ..serializers.user import UserSerializer


class Booking(APIView):
    permission_classes = (IsAuthenticated,)

    def get_space(self, space_id):
        space = get_object_or_404(Space, space_id=space_id)
        return space

    def get_agent(self, biz):
        agent = get_object_or_404(Agent, business_name=biz)
        space_agent = get_object_or_404(User, name=agent.user)
        return space_agent

    def date_object(self, date):
        return datetime.strptime(date, '%Y-%m-%d').date()

    def get_order_type_id(self, order_type):
        order = OrderType.objects.filter(order_type=order_type)[0]
        return order.order_type_id

    def post(self, request):

        user_token = getattr(request._request, 'user', None)
        user = get_object_or_404(User, user_id=user_token.id)

        data = request.data
        end_date = self.date_object(data['usage_end_date'])
        start_date = self.date_object(data['usage_start_date'])
        space_id = data["space"]
        order_type_name = data["order_type"]

        space = self.get_space(space_id)
        agent = self.get_agent(space.agent)

        agent_name = agent.name
        agent_mail = agent.email

        today = timezone.now().date()
        # //////////////////////////////////////////////////////////////////////////////////////
        def book_space():
            order_cde = order_code()
            order_data = {
                'usage_start_date': start_date,
                'usage_end_date': end_date,
                'status': 'booked',
                'transaction_code': data['transaction_code'],
                'order_code': order_cde,

                'order_type': self.get_order_type_id(order_type_name),
                'user': user_token.id,
                'space': space_id
            }

            order_serializer = OrderSerializer(data=order_data)
            if order_serializer.is_valid():
                order_serializer.save()

                # notifications
                sender = config("EMAIL_SENDER", default="space.ng@gmail.com")

                # notification for customer
                subject_customer = "ORDER COMPLETED"
                to_customer = [user.email]
                customer_content = f"Dear {user.name}, your Order has been completed. You booked space {space.name} from {start_date} to {end_date}. Thanks for your patronage"

                # notification for agent
                subject_agent = "YOU HAVE AN ORDER"
                to_agent = [agent_mail]
                agent_content = f"Dear {agent_name}, you have an order placed for your space {space.name} listed on our platform from {start_date} to {end_date}."

                send_mail(subject_agent, agent_content, sender, to_agent)
                send_mail(subject_customer, customer_content,
                          sender, to_customer)

                customer_details = {"id": user.user_id, "name": user.name,
                                    "phone_number": user.phone_number, "email": user.email}
                return Response(
                    {"payload": {**customer_details, "order_code": order_cde},
                        "message": f"Order completed"},
                    status=status.HTTP_200_OK
                )
                return Response({"message": "User not valid"})
            else:
                return Response({"error": order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    # ////////////////////////////////////////////////////////////////////////////////////////////////////

        orders = Order.objects.filter(space=space_id)
        active_orders = [
            order for order in orders if order.usage_end_date >= start_date]

        if end_date < start_date:
            return Response({"message": "End date must be a later date after start date"}, status=status.HTTP_400_BAD_REQUEST)

        if active_orders:
            for order in active_orders:
                order_end_date = order.usage_end_date
                order_type = order.order_type.order_type

                if start_date <= order_end_date:
                    print(type(order.order_type), type(
                        request.data['order_type']))
                    if order_type == "booking":
                        return Response({"message": f"Space unavailable, pick a date later than {active_orders[-1].usage_end_date} or check another space"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    if order_type == "reservation":
                        expiry_time = order.order_time + \
                            timedelta(seconds=21600)

                        return Response({"message": f"Recheck space availablity at {expiry_time} or pick another day later than {active_orders[-1].usage_end_date}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

                else:
                    return book_space()
        else:
            return book_space()

        