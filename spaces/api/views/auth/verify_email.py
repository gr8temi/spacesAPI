from rest_framework.permissions import IsAuthenticated
from django.http import Http404,JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

from ...models.user import User

class VerifyEmail(APIView):
    def check_user(self, *args):
        try:
            user = User.objects.get(token=args[0])
            return user
        except:
            return False
    
    def get(self, request):
        return Response({"message": "Email verification endpoint"})

    def post(self, request):
        token = request.data["token"]
        
        user = self.check_user(token)
        if user and user.email_verified==False:
            refresh_token = RefreshToken.for_user(user)
            user.email_verified = True
            user.save()
            return Response({
                "message": "verified",
                "token": {
                    'access': str(refresh_token.access_token)
                },
                "verify_state": user.email_verified
            }, status=status.HTTP_202_ACCEPTED)
        elif user and user.email_verified == False:
            user.email_verified = True
            user.save()
            return Response({"message": "User has already been verified"}, status=status.HTTP_410_GONE)
        return Response({"message": "You are not a registered user. Click on the link to register"})


