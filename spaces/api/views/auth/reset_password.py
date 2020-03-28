from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import bcrypt
from ...models.user import User


class ResetPassword(APIView):

    def post(self, request):
        data = request.data

        password = data['password']
        token = data['token']
        result = User.objects.get(token=token)
        
        if result:
            user = result
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user.password = hashed_password
            user.save()
            message = "Your password has successfully been reset"
            return Response({"message": message}, status=status.HTTP_200_OK)
        
        return Response({"User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
