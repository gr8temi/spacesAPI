import bcrypt
import random

customer_pw="customer"
cus_hashed = bcrypt.hashpw(customer_pw.encode('utf-8'), bcrypt.gensalt())

def customer_registration_data():
    return {
        'email': "customer@gmail.com",
        'password': cus_hashed,
        'name': "First Customer"
    }

def auth_registration_data():
    return ({
        "last_name": "test",
        "first_name": "test_name",
        "email": "test@gmail.com",
        "password": "testpassword",
        "user_type": "customer",
        "email_verification_token": "hjfdsjkfl3"
    })

def customer_login_data():
    return {
        'email': 'customer@gmail.com',
        'password': "customer"}

def agent_login_data():
    return{
        
    }
def agent_registration_data():
    return {
        "business_name": "best4less",
        "office_address":"lagos",
        "validated": False
    }

agent_pw="agent"
agent_hashed = bcrypt.hashpw(agent_pw.encode('utf-8'), bcrypt.gensalt())
def user_registration_data():
    return {
    "name": "Ola Bimbo",
    "email": f"test{random.randint(0,100)}@gmail.com",
    "phone_number": "08022211134",
    "password": agent_hashed,
    "created_at": "2019-03-15 16:14:54",
    "email_verified": True,
    "is_super": True,
    "is_customer": True,
    "is_agent": True,
    "is_active": True,
    "token": 234567,
    "updated_at": "2019-03-15 16:14:54"
}
