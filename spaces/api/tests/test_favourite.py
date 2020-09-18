import bcrypt
from django.test import TestCase
from ..models.spaces import Space
from ..models.spaces_category import SpaceCategory
from ..models.space_type import SpaceType
from ..models.user import User
from ..models.agent import Agent
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .mock_data.space_data import space_creation_data, space_category_data, space_type_data
from .mock_data.registration_data import user_registration_data, agent_registration_data
from ..models.favourite import Favourite

class FavouriteTest(APITestCase):
    def setUp(self):
        self.space_category = SpaceCategory.objects.create(
            **space_category_data())
        self.space_type = SpaceType.objects.create(
            **space_type_data(self.space_category))
        self.user = User.objects.create(**user_registration_data())
        self.agent = Agent.objects.create(
            user=self.user, **agent_registration_data())
        self.space = Space.objects.create(
            **space_creation_data(), agent=self.agent, space_type=self.space_type)
        space_info = space_creation_data()
        space_info["name"]= "WorkHome"
        self.space1 = Space.objects.create(
            **space_info, agent=self.agent, space_type=self.space_type)
        self.data = {"email": self.user.email, "password": "agent"}
        self.login_url = reverse('login')
        self.response = self.client.post(self.login_url, self.data)
        self.user_token = self.response.data["token"]['access']
        self.header = 'Bearer ' + self.user_token
        self.fav = Favourite.objects.create(user=self.user,space=self.space1)
    def test_add_favourite(self):
        add_url = reverse('favourites')

        response1 = self.client.post(add_url, data={
                                     "user": self.user.user_id, "space": self.space.space_id}, HTTP_AUTHORIZATION=self.header, format='json')
        response2 = self.client.post(add_url, data={
                                     "user": self.user.user_id, "space": self.space.space_id}, format='json')
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 401)
    
    def test_remove_favourite(self):
        remove_url = reverse("delete_favourite",kwargs={"favorite_id":f"{self.fav.favorite_id}"})

        response1 = self.client.delete(remove_url, HTTP_AUTHORIZATION=self.header, format='json')
        response2 = self.client.delete(remove_url, format='json')
        self.assertEqual(response1.status_code, 204)
        self.assertEqual(response2.status_code, 401)
