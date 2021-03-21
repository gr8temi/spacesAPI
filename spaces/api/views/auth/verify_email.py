from rest_framework.permissions import IsAuthenticated
from django.http import Http404,JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from decouple import config
from ...models.user import User

class VerifyEmail(APIView):
    def check_user(self, *args):
        try:
            user = User.objects.get(token=args[0])
            return user
        except:
            return False


    def post(self, request):
        token = request.data["token"]
        
        user = self.check_user(token)
        if user and user.email_verified==False:
            refresh_token = RefreshToken.for_user(user)
            user.email_verified = True
            email = user.email
            user.save()
            if user.is_agent == True:
                host_template = get_template('api/signup_templates/space_host_verified.html')
                html_content = host_template.render({'host_name': user.name})
            else:
                customer_template = get_template('api/signup_templates/customer_verified.html')
                html_content = customer_template.render({'guest_name': user.name})
            msg = EmailMultiAlternatives("Email Verified", html_content, config('EMAIL_SENDER'), to=[email])
            msg.attach_alternative(html_content, "text/html")
            send = msg.send()
            if send:
                return Response({
                    "message": "verified",
                    "token": {
                        'access': str(refresh_token.access_token)
                    },
                    "verify_state": user.email_verified
                }, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({
                    "message": "Failure to send email",
                }, status=status.HTTP_400_BAD_REQUEST)
        elif user and user.email_verified == True:
            return Response({"message": "User has already been verified"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "You are not a registered user."}, status=status.HTTP_404_NOT_FOUND)


