from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import bcrypt
from ...models.user import User


class ResetPassword(APIView):
    # pass
    def post(self, request):
        data = request.data

        password = data['password']
        # print(data['token'], 'wwwwwwwww')
        # print(password)
        # confirmpassword = data['confirmpassword']
        # if password:
        token = data['token']

        # if len(password) < 8:
        #     return Response({"message": "Invalid Password, password length must contain 8 characters or more"}, status=status.HTTP_400_BAD_REQUEST)

        result = User.objects.get(token=token).first()
        print(result)
        if result:
            user = result[0]
            print(user)
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user.password = hashed_password
            user.save()
            message = "Your password has been successfully reset"
            return Response({message: message}, status=status.HTTP_200_OK)
        else:
            return Response({"User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response("Both fields muust be the same")
