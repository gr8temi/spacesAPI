
def customer_registration_data():
    return ({
        "last_name": "test",
        "first_name": "test_name",
        "email": "test@gmail.com",
        "username": "testuser",
        "password": "testpassword",
        "user_type": "customer",
        "email_verification_token": "hjfdsjkfl3"
    })

def agent_registration_data():
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
     "username": "ola",
    "name": "Ola Bimbo",
    "email": "ola@gmail.com",
    "phone_number": "08022211134",
    "password": "12345",
    "created_at": "2019-03-15 16:14:54",
    "email_verified": True,
    "is_super": True,
    "is_customer": True,
    "is_agent": True,
    "is_active": True,
    "token": 234567,
    "updated_at": "2019-03-15 16:14:54"
}
