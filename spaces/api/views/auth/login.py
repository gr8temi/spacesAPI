import bcrypt
from ...models.user import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.models import TokenUser


class UserLogin(APIView):
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(username=data['username'])
            is_valid_password = bcrypt.checkpw(
                data['password'].encode('utf-8'), user.password.split("'")[1].encode('utf-8'))
            if is_valid_password:
                refresh = RefreshToken.for_user(user)
                token = {
                    'access': str(refresh.access_token),
                }

                return Response(dict(message="Login was successful", token=token), status=status.HTTP_200_OK)
            else:
                return Response(dict(error="User name or password is not valid"), status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(dict(error="User name or password is not valid"), status=status.HTTP_400_BAD_REQUEST)
