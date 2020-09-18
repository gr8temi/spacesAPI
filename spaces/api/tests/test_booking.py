import bcrypt
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .mock_data.order_data import booking_confirmed_data
from rest_framework.test import APIClient


class TestBooking(APITestCase):

    def setUp(self):
        self.data = booking_confirmed_data()
        self.url = reverse('booking')
        self.client = APIClient()

    def test_booking(self):
        
        response1 = self.client.post(
            self.url, self.data["hourly_booking"], format='json'
        )
       
        self.assertEqual(response1.status_code,200)
        response2 = self.client.post(
            self.url, self.data["hourly_booking"], format='json'
        )
        self.assertEqual(response2.status_code, 409)

    def test_old_booking(self):
        response1 = self.client.post(
            self.url, self.data["old_bookings"], format='json'
        )
        self.assertEqual(response1.status_code, 400)
    

