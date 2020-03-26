import bcrypt
from ...models.user import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_id'] = user.user_id
        # ...

        return token

class UserLogin(APIView):
    serializer_class = MyTokenObtainPairSerializer
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(username=data['username'])
            is_valid_password = bcrypt.checkpw(
                data['password'].encode('utf-8'), user.password.split("'")[1].encode('utf-8'))
            print(bool(is_valid_password))
            if is_valid_password:
                print("entered")
                refresh = RefreshToken.for_user(user)
                print(refresh)

                token = {
                    'access': str(refresh.access_token),
                }

                return Response(dict(message="Login was successful", token=token), status=status.HTTP_200_OK)
            else:
                return Response(dict(error="User name or password is not valid"), status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            raise Exception
            return Response(dict(error="User name or password is not working",), status=status.HTTP_400_BAD_REQUEST)
