import bcrypt
from django.test import TestCase
from ..models.spaces import Space
from ..models.spaces_category import SpaceCategory
from ..models.user import User
from ..models.agent import Agent
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from ..views.auth.login import UserLogin

class CreateSpaceTest(APITestCase):
    def setUp(self):
        self.old_space_count = Space.objects.count()
        self.name = "Event Hall"
        self.id = 1
        self.number_of_bookings = 1
        self.description = "An event hall for party"
        self.price = 200000
        self.space_category_id = SpaceCategory.objects.create(
            space_category="hall")
        self.location = "Lagos"
        self.availability = "available"
        self.new_user = User.objects.create( email="joe@gmail.com")
        self.agent = Agent.objects.create(
            user=self.new_user, business_name="best4less")
        self.space = Space.objects.create(name=self.name,
                                          number_of_bookings=self.number_of_bookings, agent=self.agent, description=self.description, price=self.price, space_category=self.space_category_id)

    def test_create_space(self):
        self.space.save()
        new_space_count = Space.objects.count()
        self.assertNotEqual(self.old_space_count, new_space_count)


class VIewTestCase(APITestCase):
    def setUp(self):
        password="joe"
        self.hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.new_user = User.objects.create(
             email="joe@gmail.com", password=self.hashed)
        self.new_user.save()
        self.name = "Event Hall"
        self.id = 1
        self.number_of_bookings = 1
        self.description = "An event hall for party"
        self.price = 200000
        self.space_category = SpaceCategory.objects.create(
            space_category="hall")
        self.location = "Lagos"
        self.availability = "available"
        self.agent = Agent.objects.create(
            user=self.new_user, business_name="best4less")

    def test_create(self):
        data = {'email': self.new_user.email, 'password': "joe"}
        url = reverse('login')
        response = self.client.post(url, data )
        user_token = response.data["token"]['access']
        
        # header = {'Authorization' : 'Bearer ' + user_token }
        header = 'Bearer ' + user_token
        # self.client.login(username=self.new_user.username,password="joe")
        
        space_data = {
            "number_of_bookings":self.number_of_bookings,
            "agent":self.agent.agent_id,
            "description":self.description,
            "space_category":self.space_category.category_id,
            "location":self.location,
            "name":self.name,
            "price":200
        }
        response1 = self.client.post(
            reverse('space'),space_data ,HTTP_AUTHORIZATION=header, format='json')
        self.assertEqual(response1.status_code, 201)
