import uuid
from ...models.agent import Agent
from ...models.user import User
from ...models.spaces_category import SpaceCategory


def space_creation_data():
    return {
        "name": "flora hall",
        "description": "testuser",
        "address": {"address": "Ijeoma Odika", "city": "lekki", "state": "lagos"},
        "gmap": {"lat": "6.234567", "lng": "-2.675432"},
        "number_of_bookings": 1,
        "capacity":50,
        "amount": "450000",
        "duration": "daily",
        "images":["image1"],
        "videos":["video1"],
        "amenities":["facilities"],
        "carspace": 50,
        "rules":["rules"],
        "cancellation_rules":["no-refund"]
    }

def hourly_space_data():
    return {
        "name": "dura office space",
        "description": "testuser",
        "address": {"address": "Ijeoma Odika", "city": "lekki", "state": "lagos"},
        "gmap": {"lat": "6.234567", "lng": "-2.675432"},
        "number_of_bookings": 1,
        "capacity":50,
        "amount": "450000",
        "duration": "hourly",
        "images":["image1"],
        "videos":["video1"],
        "amenities":["facilities"],
        "carspace": 50,
        "rules":["rules"],
        "cancellation_rules":["no-refund"]
    }

def monthly_space_data():
    return {
        "name": "decaspace",
        "description": "testuser",
        "address": {"address": "Ijeoma Odika", "city": "lekki", "state": "lagos"},
        "gmap": {"lat": "6.234567", "lng": "-2.675432"},
        "number_of_bookings": 1,
        "capacity":50,
        "amount": "450000",
        "duration": "monthly",
        "images":["image1"],
        "videos":["video1"],
        "amenities":["facilities"],
        "carspace": 50,
        "rules":["rules"],
        "cancellation_rules":["no-refund"]
    }

def yearly_space_data():
    return {
        "name": "our space",
        "description": "testuser",
        "address": {"address": "Ijeoma Odika", "city": "lekki", "state": "lagos"},
        "gmap": {"lat": "6.234567", "lng": "-2.675432"},
        "number_of_bookings": 1,
        "capacity":50,
        "amount": "450000",
        "duration": "yearly",
        "images":["image1"],
        "videos":["video1"],
        "amenities":["facilities"],
        "carspace": 50,
        "rules":["rules"],
        "cancellation_rules":["no-refund"]
    }
    
def extra1():
    return {"name": "AC", "cost": 500, "duration": "hourly", "space": "asdfghjk"}

def extra2(): 
    return {"name": "Bouncer", "cost": 500, "duration": "hourly", "space": "asdfghjk"}

def availability1():
    return {"day": "tuesday", "all_day": True, "open_time": "00:00", "close_time": "23:59","space": "asdfghjk"}

def availability2():
    return {"day": "monday", "all_day": True, "open_time": "08:00", "close_time": "17:00", "space": "asdfghjk"}

def availability3_1():
    return {"day": "monday", "all_day": True, "open_time": "08:00", "close_time": "17:00", "space": "dura office space"}
def availability3_2():
    return {"day": "tuesday", "all_day": True, "open_time": "08:00", "close_time": "17:00", "space": "dura office space"}
def availability3_3():
    return {"day": "wednesday", "all_day": True, "open_time": "08:00", "close_time": "17:00", "space": "dura office space"}
def availability3_4():
    return {"day": "thursday", "all_day": True, "open_time": "08:00", "close_time": "17:00", "space": "dura office space"}
def availability3_5():
    return {"day": "friday", "all_day": True, "open_time": "08:00", "close_time": "17:00", "space": "dura office space"}
def availability3_6():
    return {"day": "saturday", "all_day": True, "open_time": "08:00", "close_time": "17:00", "space": "dura office space"}
def availability3_7():
    return {"day": "sunday", "all_day": True, "open_time": "08:00", "close_time": "17:00", "space": "dura office space"}

def extras_data():
    return {
        "extras": [{"name": "AC", "cost": 500, "duration": "hourly"}, {"name": "Bouncer", "cost": 500, "duration": "hourly"}]
    }

def availability_data():
    return {
        "availability":[{"day": "Monday", "all_day": False, "open_time": "08:00", "close_time": "17:00"}, {"day": "Tuesday", "all_day": False, "open_time": "08:00", "close_time": "18:00"}],
    }

def space_category_data():
    return {
        "space_category":"Hall"
    }