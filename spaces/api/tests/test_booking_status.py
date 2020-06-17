import bcrypt
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta, datetime
import uuid
from ..views.booking import Booking
from ..models.spaces_category import SpaceCategory
from ..models.agent import Agent
from ..models.spaces import Space
from ..models.user import User
from ..models.customer import Customer
from ..models.order_type import OrderType
from ..models.order import Order
from ..helper.helper import order_code

from .mock_data.registration_data import agent_registration_data, user_registration_data
from .mock_data.order_data import order_type_booking, order_data,order_type_reservation
from .mock_data.space_data import space_category_data, space_creation_data


class TestBookingStatus(APITestCase):

    def setUp(self):
        self.user = User.objects.create(**user_registration_data())
        self.agent = Agent.objects.create(
            user=self.user, **agent_registration_data())
        self.category = SpaceCategory.objects.create(**space_category_data())
        self.space = Space.objects.create(space_category=self.category,agent=self.agent,**space_creation_data())
        self.order_type_booking = OrderType.objects.create(**order_type_booking())
        self.order_type_reservation = OrderType.objects.create(**order_type_reservation())
        self.order_booking = Order.objects.create(user=self.user,space=self.space,order_type=self.order_type_booking,order_code="234568", **order_data())
        self.order_reservation = Order.objects.create(user=self.user,space=self.space,order_type=self.order_type_reservation, order_code="234569",**order_data())

    def test_book_status(self):
        url1 = reverse('booking_status',args=[str(self.order_booking.order_code)])
        url2 = reverse('booking_status',args=[str(self.order_reservation.order_code)])
        url3 =reverse('booking_status',args=["1234kmonkh"])

        response1 = self.client.get(url1)
        response2 = self.client.get(url2)
        response3 = self.client.get(url3)
        
        self.assertEqual(response1.status_code,200)
        self.assertEqual(response2.status_code,200)
        self.assertEqual(response3.status_code,404)

