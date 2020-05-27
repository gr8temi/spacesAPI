from django.shortcuts import get_object_or_404
from abc import ABC, abstractmethod
from datetime import datetime
from ..models import spaces, agent, user
from ..models.order_type import OrderType
from ..helper.helper import order_code
from rest_framework.views import APIView


class PlaceOrder(APIView):

    def get_space(self, space_id):
        space = get_object_or_404(spaces.Space, space_id=space_id)
        return space

    def get_agent(self, biz):
        agt = get_object_or_404(agent.Agent, business_name=biz)
        space_agent = get_object_or_404(user.User, name=agt.user)
        return space_agent

    def date_object(self, date):
        return datetime.strptime(date, '%Y-%m-%d').date()

    def get_order_type_id(self, order_type):
        order = get_object_or_404(OrderType, order_type=order_type)
        return order.order_type_id
    
    @abstractmethod
    def post(self):
        pass
   