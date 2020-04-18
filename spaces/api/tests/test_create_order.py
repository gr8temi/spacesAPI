import bcrypt
from django.test import TestCase
from ..models.spaces import Space
from ..models.spaces_category import SpaceCategory
from ..models.user import User
from ..models.agent import Agent
from ..models.customer import Customer
from ..models.order import Order
from ..models.order_type import OrderType
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from ..views.auth.login import UserLogin

class CreateOrderTest(APITestCase):
    def setUp(self):
        self.old_count = Space.objects.count()

        password="user"
        self.hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        self.usage_start_date = "2020-04-12"
        self.usage_end_date = "2020-04-18"
        self.status = "booked"
        self.transaction_code = "12345abc"
        self.order_code = "54321cba"
        self.order_type = OrderType.objects.create(order_type="booking")
        self.user = User.objects.create(email="user@gmail.com", password=self.hashed)

        self.name = "Event Hall"
        self.number_of_bookings = 1
        self.description = "An event hall for party"
        self.price = 200000
        self.space_category_id = SpaceCategory.objects.create(space_category="hall")
        self.new_agent = User.objects.create( email="joe@gmail.com")
        self.agent = Agent.objects.create(
            user=self.new_agent, business_name="best4less")
        self.new_cust = User.objects.create( email="ola@gmail.com")
        self.new_cust.save()
        self.customer= Customer.objects.create(user=self.new_cust)
        self.images = ['An image url', 'Another image url']
        self.videos = ['A video url', 'Another video url']
        self.rules = ['No drinking', 'No smoking']
        self.facilities = ['Rest room', 'Changing room']
        self.space = Space.objects.create(name=self.name,
                                          number_of_bookings=self.number_of_bookings, agent=self.agent, description=self.description, price=self.price, space_category=self.space_category_id, images=self.images, videos=self.videos, rules=self.rules, facilities=self.facilities
                                        )

        self.order = Order.objects.create(usage_start_date=self.usage_start_date,
                                            usage_end_date=self.usage_end_date,
                                            status=self.status,
                                            transaction_code=self.transaction_code,
                                            order_code=self.order_code,
                                            order_type=self.order_type,
                                            user=self.user,
                                            space=self.space
                                        )

        self.order_data = {
                    'usage_start_date': "2020-16-04",
                    'usage_end_date': "2020-18-04",
                    'transaction_code': "234567",
                    'order_code': "234Spaces/234567",
                    'order_type': 1,
                    'space': "Event Hall"
                }

    def test_create_order(self):
        self.order.save()
        new_count = Order.objects.count()
        self.assertNotEqual(self.old_count, new_count)
