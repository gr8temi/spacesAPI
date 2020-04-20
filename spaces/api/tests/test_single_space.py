from rest_framework.test import APITestCase
from ..models.spaces import Space
from ..models.user import User
from ..models.agent import Agent
from ..models.spaces_category import SpaceCategory
from django.urls import reverse
from rest_framework import status


class TestSingleSpace(APITestCase):

    def setUp(self):
        self.name = "Event Hall"
        self.id = 1
        self.number_of_bookings = 1
        self.description = "An event hall for party"
        self.price = 200000
        self.space_category_id = SpaceCategory.objects.create(
            space_category="hall")
        self.location = "Lagos"
        self.new_user = User.objects.create( email="joe@gmail.com")
        self.agent = Agent.objects.create(
            user=self.new_user, business_name="best4less")
        self.images = ['An image url', 'Another image url']
        self.videos = ['A video url', 'Another video url']
        self.rules = ['No drinking', 'No smoking']
        self.facilities = ['Rest room', 'Changing room']
        self.space = Space.objects.create(name=self.name,
                                          number_of_bookings=self.number_of_bookings, agent=self.agent, description=self.description, price=self.price, space_category=self.space_category_id, images=self.images, videos=self.videos, rules=self.rules, facilities=self.facilities)
       

    def test_get_space(self):
        url = reverse("a_space", args=[self.space.space_id])
        response = self.client.get(url)
        self.assertEqual(type(response.data["payload"]),type({}))
        self.assertEqual(response.status_code,status.HTTP_200_OK )


