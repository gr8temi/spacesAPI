from ...models.user import User
from ...models.vendor import Vendor
from ...models.customer import Customer

def customer_forgot_password_data():
    return {
        "user_name": "customerDoe"
    }


def vendor_forgot_password_data():
    return {
        "user_name": "vendorDoe"
    }



def user1_registration_data():
    return {
        "user_name": "customerDoe",
        "password": "pass123",
        "user_type": "customer",
        "email_verified": False
    }

def user2_registration_data():
    return {
        "user_name": "vendorDoe",
        "password": "pass123",
        "user_type": "vendor",
    }


def customer_registration_data():
    return {
        "last_name": "Doe",
        "email": "customer@gmail.com",
        "first_name": "customer",
    }


def vendor_registration_data():
    return{
        "shop_name": "Doe",
        "email": "vendor@gmail.com",
            "account_verified": False,
        }

