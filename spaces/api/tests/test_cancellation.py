import bcrypt
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .mock_data.order_data import booking_data, cancellation_request_data
from rest_framework.test import APIClient
from ..models.order import Order
from .mock_data.registration_data import user_registration_data, agent_registration_data, customer_registration_data, customer_login_data
from ..models.customer import Customer
from ..models.agent import Agent
from ..models.user import User
from ..models.cancelation import Cancellation

class TestBookingCancellationRequest(APITestCase):

    def setUp(self):
        self.data = booking_data()
        self.url = reverse('booking_cancellation')
        self.booking = Order.objects.create(**self.data)
        self.booking_code = self.booking.order_code
        self.user_agent = User.objects.create(**user_registration_data())
        self.agent = Agent.objects.create(
            user=self.user_agent, **agent_registration_data())
        # create customer
        self.user_customer = User.objects.create(
            **customer_registration_data())
        self.customer = Customer.objects.create(user=self.user_customer)
        self.cancellation_data = {"reason": "reason is this",
                                  "customer_id": f"{self.customer.customer_id}",
                                  "agent_id": f"{self.agent.agent_id}", "booking_code": self.booking_code}
        self.client = APIClient()
        self.login_data = {**customer_login_data()}
        self.agent_login_data = {"email":self.agent.user.email, "password":"agent"}
        self.url1= reverse('login')
        self.response = self.client.post(self.url1, self.login_data)
        self.agent_login_response = self.client.post(
            self.url1, self.agent_login_data)
        self.user_token = self.response.data["token"]['access']
        self.agent_token = self.agent_login_response.data["token"]['access']
        self.header = 'Bearer ' + self.user_token
        self.header1 = 'Bearer ' + self.agent_token
        self.cancel = Cancellation.objects.create(reason="reason",customer=self.customer,agent=self.agent, booking=self.booking)

    def test_cancellation(self):
        response1 = self.client.post(self.url, self.cancellation_data, HTTP_AUTHORIZATION=self.header, format='json')
        self.assertEqual(response1.status_code, 201)

    def test_approve_cancellation(self):
        approve_url = reverse('booking_cancellation_actions',kwargs={"cancellation_id":self.cancel.cancellation_id})
        data={
            "update_type": "accept"
        }
        response2 = self.client.put(
            approve_url, data, HTTP_AUTHORIZATION=self.header1, format='json')
        self.assertEqual(response2.status_code, 200)
    def test_decline_cancellation(self):
        approve_url = reverse('booking_cancellation_actions',kwargs={"cancellation_id":self.cancel.cancellation_id})
        data={
            "update_type": "decline",
            "reason": "This is the reason"
        }
        response2 = self.client.put(
            approve_url, data, HTTP_AUTHORIZATION=self.header1, format='json')
        self.assertEqual(response2.status_code, 200)
