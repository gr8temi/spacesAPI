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

from .mock_data.space_data import space_creation_data, space_type_data
from .mock_data.registration_data import user_registration_data, agent_registration_data, customer_registration_data
from .mock_data.order_data import order_data, order_type_booking


class CreateOrderTest(APITestCase):

    def test_add(self):
        count = 2
        self.assertEqual(1+1,count)
     
