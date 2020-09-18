import bcrypt
from django.test import TestCase
from ..models.spaces import Space
from ..models.spaces_category import SpaceCategory
from ..models.space_type import SpaceType
from ..models.user import User
from ..models.agent import Agent
from ..models.customer import Customer
from ..models.availabilities import Availability
from ..models.extras import Extra
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from ..views.auth.login import UserLogin
from .mock_data.space_data import space_creation_data, space_type_data, space_category_data, extras_data, availability_data
from .mock_data.registration_data import user_registration_data, agent_registration_data, customer_registration_data, customer_login_data

class CreateSpaceTest(APITestCase):
    def setUp(self):
        self.space_category = SpaceCategory.objects.create(**space_category_data())
        self.space_type = SpaceType.objects.create(**space_type_data(self.space_category))
        self.user = User.objects.create(**user_registration_data())
        self.agent = Agent.objects.create(user=self.user, **agent_registration_data())
        self.old_space_count = Space.objects.count()

    def test_create_space(self):
        space = Space.objects.create(**space_creation_data(), agent=self.agent, space_type=self.space_type)
        new_space_count = Space.objects.count()
        self.assertNotEqual(self.old_space_count, new_space_count)


class ViewTestCase(APITestCase):
    def setUp(self):
        self.space_category = SpaceCategory.objects.create(**space_category_data())
        self.space_type = SpaceType.objects.create(
            **space_type_data(self.space_category))
        # create agent
        self.user_agent = User.objects.create(**user_registration_data())
        self.agent = Agent.objects.create(user=self.user_agent, **agent_registration_data())
        # create customer
        self.user_customer = User.objects.create(**customer_registration_data())
        self.customer = Customer.objects.create(user=self.user_customer)
        self.data = {**customer_login_data()}
        self.url = reverse('login')
        self.response = self.client.post(self.url, self.data )
        self.user_token = self.response.data["token"]['access']
        self.header = 'Bearer ' + self.user_token
        
    def test_create(self):
        
        space_data = {
            **space_creation_data(),
            **extras_data(),
            **availability_data(),
            "agent": self.agent.agent_id,
            "space_type": self.space_type.space_type_id
        }
        response1 = self.client.post(
            reverse('space'),space_data, HTTP_AUTHORIZATION=self.header, format='json')
        name = space_data['name']
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response1.data['message'], f'{name} was created successfully')
