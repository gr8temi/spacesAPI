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
from .mock_data.space_data import space_data

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
        self.new_user = User.objects.create( email="joe@gmail.com")
        self.agent = Agent.objects.create(
            user=self.new_user, business_name="best4less")
        self.images = ['An image url', 'Another image url']
        self.videos = ['A video url', 'Another video url']
        self.rules = ['No drinking', 'No smoking']
        self.facilities = ['Rest room', 'Changing room']
        # self.space = Space.objects.create(name=self.name,
        #                                   number_of_bookings=self.number_of_bookings, agent=self.agent, description=self.description, price=self.price, space_category=self.space_category_id, images=self.images, videos=self.videos, rules=self.rules, facilities=self.facilities)
        # print(self.space.rule)
    def test_create_space(self):
        space = Space.objects.create(**space_data())
        space.save()
        new_space_count = Space.objects.count()
        self.assertNotEqual(self.old_space_count, new_space_count)


class ViewTestCase(APITestCase):
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
        self.latitude = "12.567895"
        self.longitude = "0.876545"
        self.agent = Agent.objects.create(
            user=self.new_user, business_name="best4less")
        self.images = ['An image url', 'Another image url']
        self.videos = ['A video url', 'Another video url']
        self.rules = ['No drinking', 'No smoking']
        self.facilities = ['Rest room', 'Changing room']

    def test_create(self):
        data = {'email': self.new_user.email, 'password': "joe"}
        url = reverse('login')
        response = self.client.post(url, data )
        user_token = response.data["token"]['access']
        
        header = 'Bearer ' + user_token
        
        # space_data = {
        #     "number_of_bookings":self.number_of_bookings,
        #     "agent":self.agent.agent_id,
        #     "description":self.description,
        #     "space_category":self.space_category.category_id,
        #     "location":self.location,
        #     "name":self.name,
        #     "price":200,
        #     "images": self.images,
        #     "videos": self.videos,
        #     "rules": self.rules,
        #     "facilities": self.facilities,
        # }
        response1 = self.client.post(
            reverse('space'),space_data() ,HTTP_AUTHORIZATION=header, format='json')
        self.assertEqual(response1.status_code, 201)
