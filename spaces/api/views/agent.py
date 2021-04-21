import uuid
from rest_framework.views import APIView
import bcrypt
from decouple import config
from django.core.mail import send_mail
from ..models.agent import Agent
from ..models.user import User
from ..serializers.agent import AgentSerializer
from ..serializers.user import UserSerializer, UserRegisterSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from ..helper.helper import random_string_generator as token_generator, send_email
from rest_framework.decorators import permission_classes
from django.db import transaction, IntegrityError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


class AgentList(APIView):
    # permission_classes=[IsAuthenticated,]

    def get(self, request, format=None):
        queryset = Agent.objects.all()
        serializer = AgentSerializer(queryset, many=True)
        return Response(
            {"payload": serializer.data, "message": "fetch successful"},
            status=status.HTTP_200_OK,
        )


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
            return Response(
                {"payload": serializer.data, "message": "fetch successful"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @permission_classes([IsAuthenticated])
    def put(self, request, agent_id):
        agent = self.get_object(agent_id)
        if bool(agent):

            serializer = AgentSerializer(agent, data=request.data, partial=True)
            user = User.objects.get(user_id=agent.user.user_id)
            user_serializer = UserRegisterSerializer(
                user, data=request.data, partial=True
            )

            if serializer.is_valid() and user_serializer.is_valid():
                serializer.save()
                user_serializer.save()
                return Response(
                    {
                        "payload": {**serializer.data, **user_serializer.data},
                        "message": "Agent successfully updated",
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": serializer.custom_full_errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, agent_id, format=None):
        agent = self.get_object(agent_id)
        if bool(agent):
            agent.delete()
            return Response(
                {"message": "Agent successfully deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class AgentRegister(APIView):
    def get_object(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return False

    def serializeAgent(self, data, email, user, token, new_user):
        agent_serializer = AgentSerializer(data=data)
        if agent_serializer.is_valid():
            agent_serializer.save()
            agent_name = agent_serializer.data.get("business_name")
            if bool(new_user):
                user.is_agent = True
                user.save()
                email_verification_url = config("VERIFY_EMAIL_URL")
                host_template = get_template(
                    "api/signup_templates/space_host_signup.html"
                )
                host_content = host_template.render(
                    {
                        "host_name": agent_name,
                        "email_link": f"{email_verification_url}/?token={token}",
                    }
                )
                msg = EmailMultiAlternatives(
                    "Verify Email", host_content, config("EMAIL_SENDER"), to=[email]
                )
                msg.attach_alternative(host_content, "text/html")
                # send mail to the user
                send = msg.send()
                if send:
                    return Response(
                        {
                            "message": f"Space host {agent_name} successfully created",
                            "payload": agent_serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {"message": "Mail not sent"}, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {
                        "message": f"Your account has been updated successfully to a Space host",
                        "payload": agent_serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
        else:
            return Response(
                {"errors": agent_serializer.custom_full_errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request, format=None):
        with transaction.atomic():
            try:
                data = request.data
                email = data.get("email")
                check = self.get_object(email)
                hashed = ""
                if data.get("password"):
                    hashed = bcrypt.hashpw(
                        data.get("password").encode("utf-8"), bcrypt.gensalt()
                    )
                else:
                    return Response(
                        {"message": "password is needed"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                token = token_generator()
                user_data = {
                    "name": data.get("name"),
                    "email": data.get("email"),
                    "phone_number": data.get("phone_number"),
                    "password": f"${hashed}",
                    "is_agent": True,
                    "is_customer": False,
                    "token": token,
                }

                agent_data = {
                    "business_name": data.get("business_name"),
                    "office_address": data.get("office_address"),
                }

                # Check if agent already exist
                if bool(check) and bool(check.is_agent):
                    return Response(
                        {"message": f"Space host with {check.email} already Exist"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Check if User already exist but is a customer
                elif bool(check) and check.is_customer:
                    
                    new_agent_data = {**agent_data, "user": check.user_id}
                    return self.serializeAgent(
                        new_agent_data, check.email, check, token_generator(), new_user=False
                    )

                # Create new Agent
                elif not bool(check):
                    user_serializer = UserRegisterSerializer(data=user_data)
                    if user_serializer.is_valid():
                        user_serializer.save()
                        new_agent_data = {
                            **agent_data,
                            "user": user_serializer.data.get("user_id"),
                        }

                        return self.serializeAgent(
                            new_agent_data,
                            user_serializer.data.get("email"),
                            token=user_serializer.data.get("token"),
                            new_user=True,
                        )
                    else:
                        return Response(
                            {"error": user_serializer.custom_full_errors},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
            except Exception as err:
                return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)
