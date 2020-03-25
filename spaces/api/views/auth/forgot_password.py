from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
import os
from ...models.user import User
from ...models.customer import Customer
from ...models.agent import Agent
from django.core.mail import send_mail
from decouple import config
from ...helpers import random_string_generator


class ForgotPassword(APIView):
    token = random_string_generator()
    
    def post(self, request):
        data = request.data
        # print(data)
        user_name = data['username']
        # print(user_name)
        users = User.objects.filter(username = user_name)
        
        if users:
            user = users[0]
            user_id = user.id

            if user.is_customer == True:
                user = User.objects.get(id=user_id)
                email = user.email
            elif user.is_agent == True: 
                user = User.objects.get(id=user_id)
                email = user.email
            else:
                pass

            token = user.token

        else:
            return Response("Username does not exist", status=status.HTTP_400_BAD_REQUEST)
        subject = 'Reset your password'
        to = [email]
        # print(email)
        # EMAIL_SENDER="space.ng@gmail.com"
        SENDER = config("EMAIL_SENDER", default="space.ng@gmail.com")
        from_email = SENDER
        html_content = 'Click on the link below to reset your password'
        link_message = f'<a href="link to frontend with the token">Reset password</a>'
        message = "A password reset link has been sent to your Email account"

        reset_message = send_mail(subject, html_content, from_email, to, fail_silently=False, html_message=link_message)

        if reset_message:
            user.save()
            return Response({"message":message}, status=status.HTTP_200_OK)
        return Response({"message": "Mail not sent"}, status=status.HTTP_400_BAD_REQUEST)