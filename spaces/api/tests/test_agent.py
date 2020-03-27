from rest_framework.test import APITestCase
from ..models.agent import Agent
from rest_framework import status
from django.urls import reverse


class userProfileTestCase(APITestCase):
    register_agent_url = reverse('register_agent')
    all_agents_url = reverse('all_agents')

    def setUp(self):
        # create a new user making a post request to endpoint
        self.user = self.client.post(
            '/api/v1/agents/register', data={
                'username': 'john',
                'password': 'john',
                'name': 'Oluwa John Doe',
                'email': 'johndoe@gmail.com',
                'phone_number': '08090909876',
                'business_name': 'business',
                'office_address': 'lekki',

                })

    # retrieve a list of all user profiles while the request user is authenticated
    def test_userprofile_list_authenticated(self):
        response = self.client.get(register_agent_url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # check to retrieve the profile details of the authenticated user
    def test_userprofile_detail_retrieve(self):
        response = self.client.get(reverse('profile', kwargs={'username': 'john'}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # populate the user profile that was automatically created using the signals

    def test_userprofile_profile(self):
        profile_data = data={
                'name': 'Just John Doe',
                'email': 'johndoe@gmail.com',
                'phone_number': '+91129090987',
                'business_name': 'business booming',
                'office_address': 'Lekki and Ajah',

                }
        response = self.client.put(
            reverse('profile', kwargs={'username': 'john'}), data=profile_data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
