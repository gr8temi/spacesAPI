import json
from django.urls import reverse
from rest_framework import status 
from rest_framework.test import APITestCase
from .mock_data.auth_data import reset_password_data
from .mock_data.registration_data import customer_registration_data, user_registration_data
from ..models.user import User
import bcrypt

class TestResetPassword(APITestCase):
    
    def setUp(self):
        data = user_registration_data()
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        user = User.objects.create(**data)
        user.save()

    def test_user_reset_password(self):
        url = reverse("reset-password")
        
        response = self.client.post(url, reset_password_data())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        