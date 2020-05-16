from ...models.agent import Agent
from ...models.user import User
from ...models.spaces_category import SpaceCategory
from .user import user

# user = User.objects.create( email="jte@gmail.com")

# space_category = SpaceCategory.objects.create(space_category="hall")
# agent = Agent.objects.create(user=User.objects.create( email="ola@gmail.com"), business_name="best4less")

def space_data():
    return {
            "number_of_bookings": 1,
            "agent": Agent.objects.create(user=User.objects.create( email="ola@gmail.com"), business_name="best4less"),
            "description": "An event hall for party",
            "space_category": SpaceCategory.objects.create(space_category="hall"),
            "location": "Lagos",
            "longitude": 12.345678,
            "latitude": -3.567899,
            "name": "Event Hall",
            "price":200,
            "images": ['An image url', 'Another image url'],
            "videos": ['A video url', 'Another video url'],
            "rules": ['No drinking', 'No smoking'],
            "facilities": ['Rest room', 'Changing room'],
    }