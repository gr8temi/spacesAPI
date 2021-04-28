from rest_framework.views import APIView
import bcrypt
from decouple import config
from django.core.mail import send_mail
from ..models.customer import Customer
from ..models.user import User
from ..serializers.customer import CustomerSerializer, CustomerSerializerDetail
from ..serializers.user import UserSerializer, UserRegisterSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from ..helper.helper import random_string_generator as token_generator, send_email


class CustomerList(APIView):
    # permission_classes=[IsAuthenticated,]

    def get(self, request, format=None):
        queryset = Customer.objects.all()
        serializer = CustomerSerializerDetail(queryset, many=True)
        return Response({"payload": serializer.data, "message": "fetch successful"}, status=status.HTTP_200_OK)


class CustomerDetail(APIView):
    # permission_classes = [IsAuthenticated,]
    def get_object(self, customer_id):
        try:
            return Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return False

    def get(self, request, customer_id, format=None):
        customer = self.get_object(customer_id)
        if bool(customer):
            serializer = CustomerSerializerDetail(customer)
            return Response({"payload": serializer.data, "message": "fetch successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, customer_id):
        customer = self.get_object(customer_id)
        if bool(customer):

            serializer = CustomerSerializer(
                customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"payload": serializer.data, "message": "Customer successfully updated"}, status=status.HTTP_200_OK)
            return Response({"error": serializer.custom_full_errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, customer_id, format=None):
        customer = self.get_object(customer_id)
        if bool(customer):
            customer.delete()
            return Response({"message": "Customer successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)


class CustomerRegister(APIView):
    def get_object(self, email):
        try:
            email = email.lower()
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return []

    def serializeCustomer(self, data, email, token, new_user):
        email = email.lower()
        data.get('email') = data.get('email').lower()
        customer_serializer = CustomerSerializer(data=data)
        if customer_serializer.is_valid():
            customer_serializer.save()
            customer_name = User.objects.get(
                user_id=customer_serializer.data.get("user")).name
            if bool(new_user):
                email_verification_url = config("VERIFY_EMAIL_URL")
                customer_template = get_template('api/signup_templates/customer_signup.html')
                customer_content = customer_template.render({'guest_name': customer_name, "email_link":f"{email_verification_url}/?token={token}"})
                msg = EmailMultiAlternatives("Verify Email", customer_content, config('EMAIL_SENDER'), to=[email])
                msg.attach_alternative(customer_content, "text/html")
                # send mail to the user
                send = msg.send()
            if send:
                return Response({"message": f"Customer {customer_name} successfully created", "payload": customer_serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Mail not sent"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": customer_serializer.custom_full_errors}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        data = request.data
        data.get('email') = data.get('email').lower()
        email = data.get('email')
        check = self.get_object(email)
        hashed = bcrypt.hashpw(
            data['password'].encode('utf-8'), bcrypt.gensalt())
        token = token_generator()
        user_data = {
            'name': data.get('name'),
            'email': data.get('email'),
            'phone_number': data.get('phone_number'),
            'password': f'${hashed}',
            "token": token,
            "is_customer": True
        }

        customer_data = {

        }

        # Check if customer already exist
        if bool(check) and bool(check.is_customer):
            return Response({"message": f"Customer {check.name} already Exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        # Create new Customer
        elif not bool(check):
            user_serializer = UserRegisterSerializer(data=user_data)
            if user_serializer.is_valid():
                user_serializer.save()
                new_customer_data = {**customer_data,
                                     "user": user_serializer.data["user_id"]}

                return self.serializeCustomer(new_customer_data, user_serializer.data.get("email"), token=user_serializer.data["token"], new_user=True)
            else:
                return Response({"error": user_serializer.custom_full_errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Customer {check.name} Exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)


class FetchByPhoneNumber(APIView):

    def get_object(self, phone_number):
        try:
            return Customer.objects.get(user__phone_number=phone_number)
        except Customer.DoesNotExist:
            return False

    def get(self, request, phone_number):
        customer = self.get_object(phone_number)
        if not customer:
            return Response({"message": "Customer with the given phone number does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerSerializerDetail(customer)
        return Response({"payload": serializer.data, "message": "fetch successful"}, status=status.HTTP_200_OK)


class FetchByEmail(APIView):

    def get_object(self, email):
        try:
            email = email.lower()
            return Customer.objects.get(user__email=email)
        except Customer.DoesNotExist:
            return False

    def get(self, request, email):
        email = email.lower()
        customer = self.get_object(email)
        if not customer:
            return Response({"message": "Customer with the given email does not exist"},
                     status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerSerializerDetail(customer)
        return Response({"payload": serializer.data, "message": "fetch successful"}, status=status.HTTP_200_OK)
