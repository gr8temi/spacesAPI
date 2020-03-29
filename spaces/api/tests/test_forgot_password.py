import json
from django.urls import reverse
from rest_framework import status 
from rest_framework.test import APITestCase
from .mock_data.forgot_password_data import customer_forgot_password_data, agent_forgot_password_data, user1_registration_data, user2_registration_data, customer_registration_data, agent_registration_data

from ..models.customer import Customer
from ..models.agent import Agent
from ..models.user import User


class TestForgotPassword(APITestCase):

    def test_forgot_password(self):
        url = reverse('forgot-password')
    
        user = User.objects.create(**user1_registration_data())
        user.save()
        
        agent = {"username": user.username}
        
        response = self.client.post(url, agent)
        self.assertEqual(response.status_code, status.HTTP_200_OK)