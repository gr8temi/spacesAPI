import bcrypt
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta, datetime
import json
from ..views.booking import Booking
from ..models.spaces_category import SpaceCategory
from ..models.agent import Agent
from ..models.spaces import Space
from ..models.user import User
from ..models.customer import Customer
from ..models.order_type import OrderType
from ..models.availabilities import Availability
from ..models.extras import Extra
from ..helper.helper import order_code
from .mock_data.space_data import space_creation_data, space_category_data, extra1, extra2, availability1, availability2, availability3_1, availability3_2, availability3_3, availability3_4, availability3_5, availability3_6, availability3_7, hourly_space_data, monthly_space_data, yearly_space_data
from .mock_data.order_data import order_data1, order_data3, order_data4, order_extra, hourly_order_data
from .mock_data.registration_data import user_registration_data, agent_registration_data, customer_registration_data, customer_login_data
from .mock_data.order_data import order_type_booking, order_data, order_type_reservation


class TestBooking(APITestCase):

    def setUp(self):
        # create space category
        self.space_category_id = SpaceCategory.objects.create(
            **space_category_data())
        # create agent
        self.user_agent = User.objects.create(**user_registration_data())
        self.agent = Agent.objects.create(
            user=self.user_agent, **agent_registration_data())
        # create customer
        self.user_customer = User.objects.create(
            **customer_registration_data())
        self.customer = Customer.objects.create(user=self.user_customer)
        # create order_type
        self.order_type1 = OrderType.objects.create(**order_type_booking())
        self.order_type2 = OrderType.objects.create(**order_type_reservation())
        # create space
        self.space = Space.objects.create(
            **space_creation_data(), agent=self.agent, space_category=self.space_category_id)
        self.hourlyspace = Space.objects.create(
            **hourly_space_data(), agent=self.agent, space_category=self.space_category_id)
        self.monthlyspace = Space.objects.create(
            **monthly_space_data(), agent=self.agent, space_category=self.space_category_id)
        self.yearlyspace = Space.objects.create(
            **yearly_space_data(), agent=self.agent, space_category=self.space_category_id)

        self.availability = Availability.objects.create(**availability1())
        self.availability2 = Availability.objects.create(**availability2())
        self.availability3_1 = Availability.objects.create(**availability3_1())
        self.availability3_2 = Availability.objects.create(**availability3_2())
        self.availability3_3 = Availability.objects.create(**availability3_3())
        self.availability3_4 = Availability.objects.create(**availability3_4())
        self.availability3_5 = Availability.objects.create(**availability3_5())
        self.availability3_6 = Availability.objects.create(**availability3_6())
        self.availability3_7 = Availability.objects.create(**availability3_7())

        self.data = {**customer_login_data()}
        self.url = reverse('login')
        self.response = self.client.post(self.url, self.data)
        self.user_token = self.response.data["token"]['access']
        self.header = 'Bearer ' + self.user_token
        self.url2 = reverse('booking')
        self.url3 = reverse("reservation")

    def test_booking1(self):
        data1 = {
            **order_data1(),
            **order_extra(),
            'space': self.space.space_id,
            'order_type': self.order_type1,
            'user':self.user_agent.user_id,
        }

        data3 = {
            **order_data3(),
            **order_extra(),
            'space': self.space.space_id,
            'order_type': self.order_type1,
            'user': self.user_agent.user_id,
        }

        data4 = {
            **hourly_order_data(),
            **order_extra(),
            'space': self.hourlyspace.space_id,
            'order_type': self.order_type1,
            'user': self.user_agent.user_id,

        }

        data5 = {
            **order_data3(),
            **order_extra(),
            'space': self.monthlyspace.space_id,
            'order_type': self.order_type1,
            'user': self.user_agent.user_id,
        }

        data6 = {
            **order_data3(),
            **order_extra(),
            'space': self.yearlyspace.space_id,
            'order_type': self.order_type1,
            'user': self.user_agent.user_id,
        }
        response1 = self.client.post(
            self.url2, data1, HTTP_AUTHORIZATION=self.header)
        response3 = self.client.post(
            self.url2, data3, HTTP_AUTHORIZATION=self.header)
        # response4 = self.client.post(
        #     self.url2, data4, HTTP_AUTHORIZATION=self.header)
        response5 = self.client.post(
            self.url2, data5, HTTP_AUTHORIZATION=self.header)
        # response6 = self.client.post(
        #     self.url2, data6, HTTP_AUTHORIZATION=self.header)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data['message'], "Order completed")

        self.assertEqual(response3.status_code, 503)
        self.assertEqual(
            response3.data['message'], "Space unavailable, pick a date later than 2020-04-25 11:00:00+00:00 or check another space")
        # self.assertEqual(response4.status_code, 200)
        # self.assertEqual(response4.data['message'], "Order completed")

        self.assertEqual(response5.status_code, 200)
        self.assertEqual(response5.data['message'], "Order completed")

        # self.assertEqual(response6.status_code, 200)
        # self.assertEqual(response6.data['message'], "Order completed")

    def test_reservation(self):

        data = {
            **order_data4(),
            **order_extra(),
            'space': self.space.space_id,
            'order_type': self.order_type2
        }
        response1 = self.client.post(
            self.url3, data, HTTP_AUTHORIZATION=self.header)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(
            response1.data["message"], f"{self.space.name} reserved from 2020-04-27 to 2020-04-29")

        order_code = response1.data["payload"]["order_code"]
        complete_order_data = {
            'order_code': order_code,
            'transaction_code': '235467'
        }

        response2 = self.client.put(
            self.url3, complete_order_data, HTTP_AUTHORIZATION=self.header)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data["message"], "Order completed")
