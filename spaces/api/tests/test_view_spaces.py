from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from ..models.user import User

class TestViewSpace(APITestCase):


    def test_wrong_id(self):
        id = "1234567890"
        url = "/api/space"
        response = self.client.get(url+f'/{id}')

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
    
    def test_correct_id(self):
        data = {
            "username":"adams",
            "email":"adamstems@gmail.com"
        }
        new_user = User.objects.create(**data)

        url = "/api/space"
        response = self.client.get(url+f'/{new_user.id}')
        data = response.data
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(type(data),type({}))
        
class TestViewSpaces(APITestCase):
    def test_get_all_Spaces(self):
        url = "/api/spaces"
        response = self.client.get(url)
        data = response.data
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(type(data),type([]))


