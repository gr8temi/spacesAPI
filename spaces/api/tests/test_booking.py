import bcrypt
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta, datetime

from ..views.booking import Booking
from ..models.spaces_category import SpaceCategory
from ..models.agent import Agent
from ..models.spaces import Space
from ..models.user import User
from ..models.customer import Customer
from ..models.order_type import OrderType
from ..helper.helper import order_code


class TestBooking(APITestCase):

    def setUp(self):
       
        # space details
        self.space_name = "Flora Hall"
        self.number_of_bookings = 1
        self.description = "An event hall"
        self.price = 350000
        self.images = ['An image url', 'Another image url']
        self.videos = ['A video url', 'Another video url']
        self.rules = ['No drinking', 'No smoking']
        self.facilities = ['Rest room', 'Changing room']
        # create space category
        self.space_category_id = SpaceCategory.objects.create(space_category="hall")
        # create agent
        agent_pw="agent"
        self.agent_hashed = bcrypt.hashpw(agent_pw.encode('utf-8'), bcrypt.gensalt())
        self.user_agent = User.objects.create(email="agent@gmail.com", password=self.agent_hashed, name="First Agent")
        self.agent = Agent.objects.create(
            user=self.user_agent, business_name='show ltd')

        # create customer
        customer_pw="customer"
        self.cus_hashed = bcrypt.hashpw(customer_pw.encode('utf-8'), bcrypt.gensalt())
        self.user_customer = User.objects.create(email="customer@gmail.com", password=self.cus_hashed, name="First Customer")
        self.customer = Customer.objects.create(user=self.user_customer)

        # create order_type
        self.order_type1 = OrderType.objects.create(order_type="booking")
        # self.order_type2 = OrderType.objects.create(order_type="reservation")

        self.space = Space.objects.create(name=self.space_name,
                                          number_of_bookings=self.number_of_bookings, agent=self.agent, description=self.description, price=self.price, space_category=self.space_category_id, images=self.images, videos=self.videos, rules=self.rules, facilities=self.facilities
                                        )
        def date_object(date):
            return datetime.strptime(date, '%Y-%m-%d').date()

        self.order_data1 = {
                        'usage_start_date': date_object("2020-04-18"),
                        'usage_end_date': date_object("2020-04-20"),
                        'transaction_code': "234567",
                        'order_type': self.order_type1,
                        'space': self.space.space_id
                    }
        
        self.order_data2 = {
                        'usage_start_date': date_object("2020-04-21"),
                        'usage_end_date': date_object("2020-04-23"),
                        'transaction_code': "234967",
                        'order_type': self.order_type1,
                        'space': self.space.space_id
                    }

        self.order_data3 = {
                        'usage_start_date': date_object("2020-04-23"),
                        'usage_end_date': date_object("2020-04-25"),
                        'transaction_code': "234967",
                        'order_type': self.order_type1,
                        'space': self.space.space_id
                    }

        self.data = {'email': 'customer@gmail.com', 'password': "customer"}
        self.url = reverse('login')
        self.response = self.client.post(self.url, self.data)
        self.user_token = self.response.data["token"]['access']
        self.header = 'Bearer ' + self.user_token
        self.url2 = reverse('booking')
    # tests booking if no active booking exists
    def test_booking1(self):
    
        response1 = self.client.post(self.url2, self.order_data1, HTTP_AUTHORIZATION=self.header)
        response2 = self.client.post(self.url2, self.order_data2, HTTP_AUTHORIZATION=self.header)
        response3 = self.client.post(self.url2, self.order_data3, HTTP_AUTHORIZATION=self.header)
        # print(response1.data['error'])
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data['message'], "Order completed")

        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data['message'], "Order completed")

        # self.assertEqual(response3.status_code, 503)
        self.assertEqual(response3.data['message'], "Space unavailable, pick a date later than 2020-04-23 or check another space")
       
