import bcrypt
from ...models.user import User
from ...models.agent import Agent
from ...models.spaces import Space
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class UserLogin(APIView):
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(email=data['email'])

            is_valid_password = bcrypt.checkpw(
                data['password'].encode('utf-8'), user.password.split("'")[1].encode('utf-8'))
            if is_valid_password:
                
                refresh = RefreshToken.for_user(user)

                token = {
                    'access': str(refresh.access_token),
                }
                if user.is_agent == True:
                    try:
                        agent = Agent.objects.get(user=user)
                    except Exception:
                        return Response(dict(error="User not an Agent",), status=status.HTTP_400_BAD_REQUEST)
                    no_of_spaces = Space.objects.filter(agent=agent).count()
                    document = bool(agent.document)
                    return Response(dict(message="Login was successful", token=token, agent=agent.agent_id, name=user.name, user_id=user.user_id, email=user.email, phone_number=user.phone_number, no_of_spaces=no_of_spaces, document=document), status=status.HTTP_200_OK, )
                else:
                    return Response(dict(message="Login was successful", token=token, agent=False, name=user.name, user_id=user.user_id, email=user.email, phone_number=user.phone_number), status=status.HTTP_200_OK)

            else:
                return Response(dict(error="Password is not valid"), status=status.HTTP_400_BAD_REQUEST)

        except Exception as err:
            return Response(dict(error="Email is not Correct",), status=status.HTTP_400_BAD_REQUEST)
