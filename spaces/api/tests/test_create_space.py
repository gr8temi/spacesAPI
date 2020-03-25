import bcrypt
from django.test import TestCase
from ..models.spaces import Space
from ..models.spaces_category import SpaceCategory
from ..models.user import User
from ..models.agent import Agent
from ..views.add_space import CreateSpace
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.models import TokenUser


from ..serializers.space import SpaceSerializer
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..views.auth.login import UserLogin


class CreateSpaceTest(TestCase):
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
        self.new_user = User.objects.create(
            username="joe", email="joe@gmail.com")
        self.agent = Agent.objects.create(
            user=self.new_user, business_name="best4less")
        self.space = Space.objects.create(name=self.name, id=self.id,
                                          number_of_bookings=self.number_of_bookings, agent=self.agent, description=self.description, price=self.price, space_category=self.space_category_id)

    def test_create_space(self):
        self.space.save()
        new_space_count = Space.objects.count()
        self.assertNotEqual(self.old_space_count, new_space_count)


class VIewTestCase(TestCase):
    def setUp(self):
        password="joe"
        self.hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.new_user = User.objects.create(
            username="joe", email="joe@gmail.com", password=self.hashed)
        self.new_user.save()

    def test_create(self):
        data = {'username': self.new_user.username, 'password': "joe"}
        url = reverse('login')
        response = self.client.post(url, data )
        user_token = response.data['token']['access']
        # header = {'Authorization' : 'Bearer ' + user_token }
        header = 'Authorization:' + ' Bearer ' + user_token
        print(header)
        # url2 = reverse('space')
        # response1 = self.client.post(
        #     url2, header , format='json')
        # print(response1)
        # self.assertEqual(response1.status_code, 201)
        
        response1 = self.client.post(
            '/spaces/', header , format='json')
        print(response1)
        self.assertEqual(response1.status_code, 201)
