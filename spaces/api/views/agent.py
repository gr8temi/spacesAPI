import uuid
from rest_framework.views import APIView
import bcrypt
from decouple import config
from django.core.mail import send_mail
from ..models.agent import Agent
from ..models.user import User
from ..serializers.agent import AgentSerializer
from ..serializers.user import UserSerializer,UserRegisterSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from ..helper.helper import random_string_generator as token_generator, send_email
from rest_framework.decorators import permission_classes


class AgentList(APIView):
    # permission_classes=[IsAuthenticated,]

    def get(self, request, format=None):
        queryset = Agent.objects.all()
        serializer = AgentSerializer(queryset, many=True)
        return Response({"payload": serializer.data, "message": "fetch successful"}, status=status.HTTP_200_OK)


class AgentDetail(APIView):
    # permission_classes = [IsAuthenticated,]
    def get_object(self, agent_id):
        try:
            return Agent.objects.get(agent_id=agent_id)
        except Agent.DoesNotExist:
            return False

    def get(self, request, agent_id, format=None):
        agent = self.get_object(agent_id)
        if bool(agent):
            serializer = AgentSerializer(agent)
            return Response({"payload": serializer.data, "message": "fetch successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    @permission_classes([IsAuthenticated])
    def put(self, request, agent_id):
        agent = self.get_object(agent_id)
        if bool(agent):

            serializer = AgentSerializer(
                agent, data=request.data, partial=True)
            user = User.objects.get(user_id=agent.user.user_id)
            user_serializer = UserRegisterSerializer(
                user, data=request.data, partial=True)

            if serializer.is_valid() and user_serializer.is_valid():
                serializer.save()
                user_serializer.save()
                return Response({"payload": {**serializer.data, **user_serializer.data}, "message": "Agent successfully updated"}, status=status.HTTP_200_OK)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, agent_id, format=None):
        agent = self.get_object(agent_id)
        if bool(agent):
            agent.delete()
            return Response({"message": "Agent successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class AgentRegister(APIView):
    def get_object(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return []

    def serializeAgent(self, data, email, token, new_user):
        agent_serializer = AgentSerializer(data=data)
        if agent_serializer.is_valid():
            agent_serializer.save()
            agent_name = agent_serializer.data["business_name"]
            if bool(new_user):

                email_verification_url = config("VERIFY_EMAIL_URL")
                message = "Registration was successful"
                customer_message_details = {
                    'subject': '234Spaces Space host email verification',
                    'text_content': "You are welcome on board.",
                    'to': [email],
                    'from_email': config("EMAIL_SENDER"),
                    'html_content': 'Welcome on board, complete your registration by clicking the link below',
                    'link_message': f'Welcome on board </br> Click on this <a href="{email_verification_url}/?token={token}">Link</a> to verify'

                }
                # send mail to the user
                send = send_email(customer_message_details)
            if send:
                return Response({"message": f"Space host {agent_name} successfully created", "payload": agent_serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Mail not sent"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"errors": agent_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        data = request.data
        email = data['email']
        check = self.get_object(email)

        hashed = bcrypt.hashpw(
            data['password'].encode('utf-8'), bcrypt.gensalt())
        token = token_generator()
        user_data = {
            'name': data['name'],
            'email': data['email'],
            'phone_number': data['phone_number'],
            'password': f'${hashed}',
            'is_agent': True,
            'is_customer': False,
            "token": token
        }

        agent_data = {
            'business_name': data["business_name"],
            'office_address': data["office_address"],
        }

        # Check if agent already exist
        if bool(check) and bool(check.is_agent):
            return Response({"message": f"Space host with {check.email} already Exist"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if User already exist but is a customer
        elif bool(check) and check.is_customer:
            new_agent_data = {**agent_data,
                              "user": check["user_id"]}
            return self.serializeAgent(new_agent_data)

        # Create new Agent
        elif not bool(check):
            user_serializer = UserRegisterSerializer(data=user_data)
            if user_serializer.is_valid():
                user_serializer.save()
                new_agent_data = {**agent_data,
                                  "user": user_serializer.data["user_id"]}

                return self.serializeAgent(new_agent_data, user_serializer.data["email"], token=user_serializer.data["token"], new_user=True)
            else:
                return Response({"errorr": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return
