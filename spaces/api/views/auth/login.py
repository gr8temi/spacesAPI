import bcrypt
from ...models.user import User
from ...models.agent import Agent
from ...models.customer import Customer
from ...models.spaces import Space
from ...models.subscription import SubscriptionPerAgent
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q


class UserLogin(APIView):
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(email=data['email'])

            is_valid_password = bcrypt.checkpw(
                data['password'].encode('utf-8'), user.password.split("'")[1].encode('utf-8'))
            if is_valid_password:
                # if user.email_verified is False:
                #     return Response({"message": "User is not verified. kindly verify yourself"}, status=status.HTTP_400_BAD_REQUEST) 
                refresh = RefreshToken.for_user(user)

                token = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                if user.is_agent == True:
                    try:
                        agent = Agent.objects.get(user=user)
                    except Exception:
                        return Response(dict(error="User not an Agent",), status=status.HTTP_400_BAD_REQUEST)
                    no_of_spaces = Space.objects.filter(agent=agent).count()
                    document = bool(agent.document)
                    date_of_birth = user.date_of_birth
                    profile_picture_url = user.profile_url
                    social_links = user.social_links
                    plan = agent.plans
                    if plan == "subscription":
                        subscriptions = SubscriptionPerAgent.objects.filter(
                            Q(agent=agent) & ~Q(next_due_date=None))
                        if subscriptions:

                            last_subscription = max(
                                subscriptions, key=lambda subscription: subscription.next_due_date)

                            space_host_plan = {
                                "subscription_plan": last_subscription.subscription.subscription_plan,
                                "subscription_type": last_subscription.subscription.subscription_type,
                                "next_due_date": last_subscription.next_due_date,
                                "recurring": last_subscription.recurring,
                                "name": "subscription"
                            }
                        else:
                            space_host_plan = {
                                "name": "subscription"
                            }
                    else:
                        space_host_plan = {
                            "name": "commission"
                        }
                    return Response(dict(message="Login was successful", token=token, agent=agent.agent_id, name=user.name, user_id=user.user_id, email=user.email, phone_number=user.phone_number, no_of_spaces=no_of_spaces, document=document, date_of_birth=date_of_birth,
                                         profile_picture_url=profile_picture_url,
                                         social_links=social_links, plan=space_host_plan, business_name=agent.business_name), status=status.HTTP_200_OK, )
                else:
                    try:
                        customer_id = Customer.objects.get(
                            user=user).customer_id
                    except Customer.DoesNotExist:
                        customer_id = False
                    return Response(dict(message="Login was successful", token=token, agent=False, customer_id=customer_id, name=user.name, user_id=user.user_id, email=user.email, phone_number=user.phone_number), status=status.HTTP_200_OK)

            else:
                return Response(dict(error="Invalid login details"), status=status.HTTP_400_BAD_REQUEST)

        except Exception as err:
            print(err)
            return Response(dict(error="invalid login",), status=status.HTTP_400_BAD_REQUEST)
