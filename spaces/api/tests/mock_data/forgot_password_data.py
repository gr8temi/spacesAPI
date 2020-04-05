from ...models.user import User
from ...models.agent import Agent
from ...models.customer import Customer

def customer_forgot_password_data():
    return {
        "user": 2
    }


def agent_forgot_password_data():
    return {
        "user": 1
    }



def user1_registration_data():
    return {
        "name": "Ade Wale",
        "email": "ade@gmail.com",
        "phone_number": "08011122234",
        "password": "12345",
        "created_at": "2019-01-12 15:12:34",
        "email_verified": True,
        "is_super": False,
        "is_customer": False,
        "is_agent": True,
        "is_active": False,
        "token": 234567,
        "updated_at": "2019-01-12 15:12:34"
    }



def user2_registration_data():
    return {
        "username": "ola",
        "name": "Ola Bimbo",
        "email": "ola@gmail.com",
        "phone_number": "08022211134",
        "password": "12345",
        "created_at": "2019-03-15 16:14:54",
        "email_verified": True,
        "is_super": False,
        "is_customer": True,
        "is_agent": False,
        "is_active": False,
        "token": 234567,
        "updated_at": "2019-03-15 16:14:54"
    }


def customer_registration_data():
    return {
        "user": 2
    }


def agent_registration_data():
    return{
        "user": 1,
        "business_name": "Crown Housings",
        "office_address": "1, Familoni Street",
        "validated": False,
        "updated_at": "2019-01-12 15:12:34",
        "created_at": "2019-01-12 15:12:34"
    }

