from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from ...models.user import User
from ...models.customer import Customer
from ...models.agent import Agent
from django.core.mail import send_mail
from decouple import config
from ...helpers import random_string_generator
from django.shortcuts import get_object_or_404


class ForgotPassword(APIView):
    
    def post(self, request):

        data = request.data
        user_name = data["username"]
        user = get_object_or_404(User, username=user_name)
        
        if not user:
            return Response("Username does not exist", status=status.HTTP_400_BAD_REQUEST)

        user_token = user.token
        user_id = user.id
        user_email = user.email
    
        subject = 'Reset your password'
        to = [user_email]
        SENDER = config("EMAIL_SENDER", default="space.ng@gmail.com")
        from_email = SENDER
        html_content = 'Click on the link below to reset your password'
        link_message = f'<a href="link to frontend with the user_token">Reset password</a>'
        message = "A password reset link has been sent to your Email account"

        reset_message = send_mail(subject, html_content, from_email, to, fail_silently=False, html_message=link_message)
        print(reset_message)
        if reset_message:
            user.save()
            return Response({"message":message}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Mail not sent"}, status=status.HTTP_400_BAD_REQUEST)