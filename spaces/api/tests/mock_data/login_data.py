from .user import user


def login_data():
    return {'email': user().email, 'password': "joe"}