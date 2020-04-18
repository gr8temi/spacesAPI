from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from datetime import date, timedelta, datetime
from rest_framework.permissions import IsAuthenticated
from decouple import config
from django.core.mail import send_mail
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django.utils import timezone

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

    def getSpace(self, name):
        space = get_object_or_404(Space, name=name)
        return space

    def getAgent(self, biz):
        agent = get_object_or_404(Agent, business_name=biz)
        space_agent = get_object_or_404(User, name=agent.user)
        return space_agent


    def post(self, request):

        user_token = getattr(request._request, 'user', None)
        user = get_object_or_404(User, user_id=user_token.id)

        data = request.data
        end_date = data['usage_end_date']
        start_date = data['usage_start_date']
        space_name = data["space"]
        order_type_name = data["order_type"]

        space = self.getSpace(space_name)
        space_id = space.space_id

        agent = self.getAgent(space.agent)
        agent_name = agent.name
        agent_mail = agent.email

        order_type = OrderType.objects.get(order_type=order_type_name)

        # check order table for chosen space, check enddate of all status with booked or reserve
        today = timezone.now().date()
        # order status is either active or concluded
        # the line below shld return orders for the particular space that is active
        orders = Order.objects.filter(space=space_id)
        # active_orders will return an array of orders that are booked or reserved.
        active_orders = [order for order in orders if order.usage_end_date > today]
        # print(active_orders)
        if active_orders:
            for order in active_orders:
                type = order.order_type
                order_end_date = order.usage_end_date
    
                if type == "booking":
                    # User should pick another time or check another space.
                    return Response({"message": f"Space unavailable, pick a date later than {order_end_date} or check another space"})
                if type == "reservation":
                    expiry_time = order.order_time + timedelta(seconds=21600)

                    # Tell customer to check back after the reserved expiry time or pick a date later than usage_end_date
                    return Response({"message": f"Recheck space availablity at {expiry_time} or pick another day later than {end_date}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            order_data = {
                'usage_start_date': start_date,
                'usage_end_date': end_date,
                'status': 'booked',
                'transaction_code': data['transaction_code'],
                'order_code': order_code(),
            
                'order_type': order_type.order_type_id,
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
                customer_content = f"Dear {user.name}, your Order has been completed. You booked space {space_name} from {start_date} to {end_date}. Thanks for your patronage"

                # notification for agent
                subject_agent = "YOU HAVE AN ORDER"
                to_agent = [agent_mail]
                agent_content = f"Dear {agent_name}, you have an order placed for your space {space.name} listed on our platform from {start_date} to {end_date}."

                send_mail(subject_customer, customer_content, sender, to_customer)
                send_mail(subject_agent, agent_content, sender, to_agent)
                
                return Response({"message": "Order completed"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

