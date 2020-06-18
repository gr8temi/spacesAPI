import bcrypt

def auth_data():
    return {
        "email": "spaces234@gmail.com",
        "password": "testpassword"
    }
pwd = "testpassword"
hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

def auth_reg():
    return {
        "email": "spaces234@gmail.com",
        "password": pwd,
        "name": "spaces"
    }
def reset_password_data():
    return {
        "token": 234567,
        "password": "12345"
    }
