import json
from django.urls import reverse
from rest_framework import status 
from rest_framework.test import APITestCase
from .mock_data.forgot_password_data import customer_forgot_password_data, agent_forgot_password_data, user1_registration_data, user2_registration_data, customer_registration_data, agent_registration_data

from ..models.customer import Customer
from ..models.agent import Agent
from ..models.user import User


class TestForgotPassword(APITestCase):
    url = reverse('forgot_password')

    def test_customer_forgot_password(self):
        # setup
        user = User.objects.create(**user2_registration_data())
        user.save()
        customer = Customer.objects.create(user=user)
        # print(customer)
        customer.username = {'username': user.username}
        # print(dict(customer))
        response = self.client.post(self.url, customer.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_forgot_password(self):
        # pass
        # setup
        user2 = User.objects.create(**user1_registration_data())
        user2.save()
        agent = Agent.objects.create(user=user2)
        agent.username = {'username': user2.username}

        response = self.client.post(self.url, agent.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)