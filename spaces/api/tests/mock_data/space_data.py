import uuid
from ...models.agent import Agent
from ...models.user import User
from ...models.spaces_category import SpaceCategory


def space_creation_data():
    return {
        "name": "asdfghjk",
        "description": "testuser",
        "address": {"address": "Ijeoma Odika", "city": "lekki", "state": "lagos"},
        "gmap": {"lat": "6.234567", "lng": "-2.675432"},
        "number_of_bookings": 1,
        "capacity":50,
        "amount": "450000",
        "duration": "weekly",
        "images":["image1"],
        "videos":["video1"],
        "amenities":["facilities"],
        "carspace": 50,
        "rules":["rules"],
        "cancellation_rules":["no-refund"]
    }

def extras_data():
    return {
        "extras": [{"name": "AC", "cost": 500, "duration": "hourly"}, {"name": "Bouncer", "cost": 500, "duration": "hourly"}]
    }

def availability_data():
    return {
        "availability":[{"day": "monday", "all_day": True, "open_time": "8:00", "close_time": "17:00"}, {"day": "tuesday", "all_day": False, "open_time": "", "close_time": ""}],
    }

def space_category_data():
    return {
        "space_category":"Hall"
    }