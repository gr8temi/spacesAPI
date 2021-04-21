from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from ...models.user import User
from ...models.customer import Customer
from ...models.agent import Agent
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from decouple import config
from ...helpers import random_string_generator
from django.shortcuts import get_object_or_404
from ...helpers import random_string_generator

class ForgotPasswordToken(APIView):

    def post(self, request):
        data = request.data
        email = data.get("email")
        user = get_object_or_404(User, email=email)
        token = random_string_generator()
        
        if not user:
            return Response("Username does not exist", status=status.HTTP_400_BAD_REQUEST)
        user.token = token
        user_id = user.user_id
        user_email = user.email

        subject = 'Reset your password'
        to = [user_email]
        SENDER = config("EMAIL_SENDER", default="space.ng@gmail.com")
        sender = SENDER
        html_content = 'Click on the link below to reset your password'
        link_message = f'token: {token}'
        message = "A password reset token has been sent to your Email account"

        user_template = get_template('api/forgot_password/forgot_password_token.html')
        user_content = user_template.render({'username': user.name, 'reset_password_token': token})
        msg = EmailMultiAlternatives(subject, user_content, sender, to=to)
        msg.attach_alternative(user_content, 'text/html')

        reset_message = msg.send()

        if reset_message:
            user.save()
            return Response({"message":message}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Mail not sent"}, status=status.HTTP_400_BAD_REQUEST)
