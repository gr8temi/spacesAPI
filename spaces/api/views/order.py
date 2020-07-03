from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from abc import ABC, abstractmethod
from datetime import datetime
from ..models import spaces, agent, user
from ..models.order_type import OrderType
from ..helper.helper import order_code
from rest_framework.views import APIView


class PlaceOrder(APIView):

    def get_space(self, space_id):
        try:
            space = get_object_or_404(spaces.Space, space_id=space_id)
            return space
        except:
            return False

    def get_agent(self, biz):
        try:
            agt = get_object_or_404(agent.Agent, business_name=biz)
            space_agent = get_object_or_404(user.User, name=agt.user)
            return space_agent
        except:
            return Response({"message": "Agent not found"})

    def date_object(self, date):
        return datetime.strptime(date, '%Y-%m-%d %H:%M')

    def get_order_type_id(self, order_type):
        try:
            order = get_object_or_404(OrderType, order_type=order_type)
            return order.order_type_id
        except:
            return False
        
    def check_all_day(self, av, day):  
        for each_day_availability in av:
            if each_day_availability['day'].capitalize() == day:
                if each_day_availability['all_day'] == True:
                    return True
                else:
                    return ([each_day_availability['open_time'], each_day_availability['close_time']])
    
    def invalid_time(self, start, end):
            if end < start:
                return False
            else:
                return True
    
    @abstractmethod
    def post(self):
        pass
   