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


from ..models.user import User
from ..models.agent import Agent
from ..models.spaces import Space
from ..models.order import Order
from ..models.order_type import OrderType
from ..helper.helper import order_code
from ..serializers.order import OrderSerializer
from .order import PlaceOrder


class Reservation(PlaceOrder, APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        user = request.user
        customer = get_object_or_404(User, user_id=user.id)

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
        now = timezone.now()
        reservation_expiry = now + timedelta(seconds = 21600)
        order_cde = order_code()

    # ////////////////////////////////////////////////////////////////////////////////////////////////
        def make_reservation():
        
            order_data = {
                'usage_start_date': start_date,
                'usage_end_date': end_date,
                'status': 'pending',
                'transaction_code': "none",
                'order_code': order_cde,

                'order_type': self.get_order_type_id(order_type_name),
                'user': user.id,
                'space': space_id
            }

            order_serializer = OrderSerializer(data=order_data)
            if order_serializer.is_valid():
                order_serializer.save()

                sender = config("EMAIL_SENDER", default="space.ng@gmail.com")

                # notification for customer
                subject_customer = "SPACE RESERVED"
                to_customer = [customer.email]
                customer_content = f"Dear {customer.name}, You reserved space {space.name} for use from {start_date} to {end_date}, your order code is {order_cde}. Kindly proceed to make payment and complete order by supplying your order code upon login before {reservation_expiry}. Thanks for your patronage"

                send_mail(subject_customer, customer_content,
                        sender, to_customer)

                customer_details = {"id": customer.user_id, "name": customer.name,
                                    "phone_number": customer.phone_number, "email": customer.email}
                return Response(
                    {"payload": {**customer_details, "booking_start_date": start_date, "booking_end_date": end_date, "order_code": order_cde},
                        "message": f"{space.name} reserved from {start_date} to {end_date}"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"error": order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
              
    # ////////////////////////////////////////////////////////////////////////////////////////////////

        #  check if date selected is available
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
                    if order_type == "booking":
                        return Response({"message": f"Space unavailable, pick a date later than {active_orders[-1].usage_end_date} or check another space"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    if order_type == "reservation":
                        expiry_time = order.order_time + \
                            timedelta(seconds=21600)

                        return Response({"message": f"Recheck space availablity at {expiry_time} or pick another day later than {active_orders[-1].usage_end_date}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

                else:
                    return make_reservation()
        else:
            return make_reservation()

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

                    sender = config("EMAIL_SENDER", default="space.ng@gmail.com")
                    subject_agent = "YOU HAVE A RESERVED ORDER"
                    to_agent = [agent.email]
                    agent_content = f"Dear {agent.name}, space {space.name} listed on our platform has been reser from {order.usage_start_date} to {order.usage_end_date}."

                    subject_customer2 = "ORDER COMPLETED"
                    to_customer = [customer.email]
                    customer_content2 = f"Dear {customer.name}, Your order {order_code} for {space.name} has been completed. Thanks for your patronage"


                    send_mail(subject_agent, agent_content, sender, to_agent)
                    send_mail(subject_customer2, customer_content2, sender, to_customer)

                    return Response({"message": "Order completed", "status": f"{order.status}"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Kindly make payment to proceed"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Provide order code to proceed'})
        else:
            return Response({"message": "Reservation has expired, click on booking link to make a fresh booking"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        