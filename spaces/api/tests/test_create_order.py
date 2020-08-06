import bcrypt
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from ..models.spaces import Space
from ..models.spaces_category import SpaceCategory
from ..models.user import User
from ..models.agent import Agent
from ..models.order import Order
from ..models.order_type import OrderType

from .mock_data.space_data import space_creation_data, space_category_data
from .mock_data.registration_data import user_registration_data, agent_registration_data, customer_registration_data
from .mock_data.order_data import order_data, order_type_booking

# class CreateOrderTest(APITestCase):
#     def setUp(self):
#         self.old_count = Space.objects.count()
#         self.order_type = OrderType.objects.create(**order_type_booking())
#         self.order_code = "54321cba"
#         self.space_category_id = SpaceCategory.objects.create(**space_category_data())
#         self.user = User.objects.create(**user_registration_data())
#         self.agent = Agent.objects.create(user=self.user, **agent_registration_data())
#         self.space = Space.objects.create(**space_creation_data(), agent=self.agent, space_category=self.space_category_id)
#         self.order = Order.objects.create(**order_data(), order_code = self.order_code, order_type=self.order_type,user=self.user,space=self.space)

#     def test_create_order(self):
#         self.order.save()
#         new_count = Order.objects.count()
#         self.assertNotEqual(self.old_count, new_count)

class CreateOrderTest(APITestCase):

    def test_add(self):
        count = 2
        self.assertEqual(1+1,count)
     
