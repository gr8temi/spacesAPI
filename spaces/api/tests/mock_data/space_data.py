import uuid
from ...models.agent import Agent
from ...models.user import User
from ...models.spaces_category import SpaceCategory


def space_creation_data():
    return {
        "number_of_bookings": 1,
        "description": "testuser",
        "price": "testpassword",
        "location": "customer",
        "longitude": 12.345678,
        "latitude": -3.567899,
        "name": "hjfdsjkfl3",
        "images":["image1"],
        "videos":["video1"],
        "facilities":["facilities"],
        "rules":["rules"],
        "cancellation_rules":["no-refund"],
        "capacity":50,
        "availability":[{"day": "monday", "all_day": True, "opening_time": "8am", "closing_time": "5pm"}]
    }

def space_category_data():
    return {
        "space_category":"Hall"
    }