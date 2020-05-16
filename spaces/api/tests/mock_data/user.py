from ...models.user import User


def user():
    return User.objects.create( email="jae@gmail.com")