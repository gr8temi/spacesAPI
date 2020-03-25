import json
from django.urls import reverse
from rest_framework import status 
from rest_framework.test import APITestCase
from .mock_data.auth_data import reset_password_data
from .mock_data.registration_data import customer_registration_data, user_registration_data
from ..models.user import User
import bcrypt

class TestResetPassword(APITestCase):
    pass
    url = reverse("reset_password")

    def setUp(self):
        data = user_registration_data()
        hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        token = 'randomtoken'
        user = User.objects.create(
            username=data['username'],
            password=hashed,
            token=token,
            is_customer = True
        )
        user.save()

    def test_user_reset_password(self):
        response = self.client.post(self.url, reset_password_data())
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        