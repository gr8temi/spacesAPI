
def customer_registration_data():
    return {
        "last_name": "test",
        "first_name": "test_name",
        "email": "test@gmail.com",
        "username": "testuser",
        "password": "testpassword",
        "user_type": "customer",
        "email_verification_token": "hjfdsjkfl3"
    }

def vendor_registration_data():
    return {
        "shop_name": "best4less",
        "email": "test@gmail.com",
        "username": "testuser",
        "password": "testpassword",
        "user_type": "vendor",
        "email_verification_token": "hjfdsjkfl3"
    }
    
def user_registration_data():
    return {
    "id":8,
    "user_name": "ola",
    "password": "hello",
    "user_type": "customer",
    "email_verified":False,
    "email_verification_token":"123456"
}
