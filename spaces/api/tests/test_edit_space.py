import bcrypt
from django.test import TestCase
from ..models.spaces import Space
from ..models.spaces_category import SpaceCategory
from ..models.user import User
from ..models.agent import Agent
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .mock_data.space_data import space_creation_data, space_category_data
from .mock_data.registration_data import user_registration_data, agent_registration_data


class EditSpaceTest(APITestCase):
    def setUp(self):
        self.space_category = SpaceCategory.objects.create(
            **space_category_data())
        self.user = User.objects.create(**user_registration_data())
        self.agent = Agent.objects.create(
            user=self.user, **agent_registration_data())
        self.space = Space.objects.create(
            **space_creation_data(), agent=self.agent, space_category=self.space_category)
        self.data = {"email":self.user.email, "password":"agent"}
        self.login_url = reverse('login')
        self.response = self.client.post(self.login_url, self.data)
        self.user_token = self.response.data["token"]['access']
        self.header = 'Bearer ' + self.user_token

    def test_edit_space(self):
        space_id = self.space.space_id
        capacity = 3000

        edit_url = reverse('edit_space', kwargs={"space_id":space_id})

        response1 = self.client.patch(edit_url, data={"capacity": capacity},HTTP_AUTHORIZATION=self.header, format='json')
        self.assertEqual(response1.status_code, 200)
