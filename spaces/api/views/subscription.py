import uuid
from datetime import datetime, timedelta

from django.utils import timezone
from django.db import transaction, IntegrityError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView, DestroyAPIView

from ..permissions.is_agent_permission import UserIsAnAgent
from ..helper.helper import reference_code
from ..models.subscription import Subscription, SubscriptionPerAgent, BillingHistory
from ..models.agent import Agent
from ..serializers.subscription import (
    SubscriptionSerializer,
    SubPerAgentSerializer,
    BillHistSerializer,
)
from ..serializers.agent import AgentSerializer
from spaces.paystack import paystack


class Subscribe(APIView):

    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def post(self, request):
        data = request.data
        subscription_type = data.get("subscription_type")
        subscription_plan = data.get("subscription_plan")
        agent = data.get("agent")
        recurring = data.get("recurring", False)
        reference = reference_code()
        try:
            subscription = Subscription.objects.get(
                subscription_type=subscription_type, subscription_plan=subscription_plan
            )
        except Subscription.DoesNotExist:
            return Response(
                {"message": "Subscription type selected does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = SubPerAgentSerializer(
            data={
                "subscription": f"{subscription.subscription_id}",
                "recurring": recurring,
                "reference_code": reference,
                "agent": agent,
            }
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Subscription created successfully expecting update on payment",
                    "payload": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "message": "Error processing subscription",
                    "payload": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get(self, request):
        queryset = Subscription.objects.all()
        serializer = SubscriptionSerializer(queryset, many=True)
        new_obj = {}
        for data in serializer.data:
            if data["subscription_plan"] in new_obj:
                new_obj[data["subscription_plan"]] = [
                    *new_obj[data["subscription_plan"]],
                    data,
                ]
            else:
                new_obj[data["subscription_plan"]] = [data]

        return Response(
            {"message": "Subscriptions Fetched", "payload": new_obj},
            status=status.HTTP_200_OK,
        )


class SubscribeActions(APIView):

    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def get(self, request, agent_id):
        subscriptions = SubscriptionPerAgent.objects.filter(
            agent__agent_id=uuid.UUID(agent_id), next_due_date__gt=timezone.now()
        )
        current_subscription = min(
            subscriptions,
            key=lambda subscription: subscription.next_due_date,
        )
        all_subscriptions = SubPerAgentSerializer(subscriptions, many=True).data
        current_subscription = SubPerAgentSerializer(current_subscription).data
        if all_subscriptions:
            return Response(
                {
                    "message": "Subscriptions fetched successfully",
                    "payload": {
                        "current_subscription": current_subscription,
                        "all_subscriptions": all_subscriptions,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "No active subscriptions was fetched fot this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, reference_code):
        try:
            with transaction.atomic():
                verified_payment = paystack.transaction.verify(reference=reference_code)
                try:
                    agent_subscription = SubscriptionPerAgent.objects.get(
                        reference_code=reference_code
                    )
                except SubscriptionPerAgent.DoesNotExist:
                    return Response(
                        {"message", "Subscription does not exist"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                previous_paid_at = agent_subscription.paid_at
                if (
                    previous_paid_at is not None
                    and previous_paid_at
                    >= datetime.strptime(
                        verified_payment["data"]["paid_at"].split(".")[0],
                        "%Y-%m-%dT%H:%M:%S",
                    )
                    and agent_subscription.paid == True
                ):
                    return Response(
                        {
                            "message": f"Payment made is already active and expires {agent_subscription.next_due_date}"
                        }
                    )

                if (
                    previous_paid_at is not None
                    and previous_paid_at
                    >= datetime.strptime(
                        verified_payment["data"]["paid_at"].split(".")[0],
                        "%Y-%m-%dT%H:%M:%S",
                    )
                    and agent_subscription.paid == False
                ):
                    return Response(
                        {
                            "message": f"This payment has either expired at this date {agent_subscription.next_due_date}"
                        }
                    )

                if verified_payment["status"]:
                    authorization_code = verified_payment["data"]["authorization"][
                        "authorization_code"
                    ]
                    subscription_type = agent_subscription.subscription_type()
                    subscriptions_expiry_dates = list(
                        SubscriptionPerAgent.objects.filter(
                            agent=agent_subscription.agent
                        ).values_list("next_due_date")
                    )
                    if subscriptions_expiry_dates:
                        try:
                            last_expiry_date = max(
                                [
                                    subscription
                                    for subscription in subscriptions_expiry_dates
                                    if subscription[0] is not None
                                ]
                            )[0]
                        except:
                            last_expiry_date = None
                    else:
                        last_expiry_date = None
                    if (
                        last_expiry_date is not None
                        and last_expiry_date > timezone.now()
                    ):
                        start_time = last_expiry_date + timedelta(days=1)
                    else:
                        start_time = datetime.now()

                    if subscription_type == "monthly":
                        due_date = SubscriptionPerAgent.objects.monthly_subscription(
                            start_time
                        )
                    elif subscription_type == "quarterly":
                        due_date = SubscriptionPerAgent.objects.quarterly_subscription(
                            start_time
                        )
                    elif subscription_type == "bi-annually":
                        due_date = SubscriptionPerAgent.objects.bi_annual_subscription(
                            start_time
                        )
                    elif subscription_type == "yearly":
                        due_date = SubscriptionPerAgent.objects.annual_subscription(
                            start_time
                        )
                    elif subscription_type == "per minute":
                        due_date = SubscriptionPerAgent.objects.minute_subscription(
                            start_time
                        )
                    else:
                        return Response(
                            {"message", "Subscription type selected does not exist"},
                            status=status.HTTP_404_NOT_FOUND,
                        )

                    agent_subscription.next_due_date = due_date
                    agent_subscription.paid = True
                    agent = Agent.objects.get(
                        agent_id=agent_subscription.agent.agent_id
                    )
                    agent.plans = "subscription"
                    agent.save()
                    agent_subscription.paid_at = datetime.strptime(
                        verified_payment["data"]["paid_at"].split(".")[0],
                        "%Y-%m-%dT%H:%M:%S",
                    )
                    agent_subscription.authorization_code = authorization_code
                    agent_subscription.amount = verified_payment["data"]["amount"] / 100
                    agent_subscription.save()

                    all_agent_subscriptions = SubscriptionPerAgent.objects.filter(
                        agent=agent_subscription.agent, next_due_date__gt=timezone.now()
                    )
                    current_subscription = min(
                        all_agent_subscriptions,
                        key=lambda subscription: subscription.next_due_date,
                    )

                    return Response(
                        {
                            "message": f"Subscription successful. Next due date is {due_date}",
                            "payload": {
                                "due_date": agent_subscription.next_due_date,
                                "subscription_type": agent_subscription.subscription.subscription_type,
                                "subscription_plan": agent_subscription.subscription.subscription_plan,
                                "current_subscription_type": current_subscription.subscription.subscription_type,
                                "current_subscription_plan": current_subscription.subscription.subscription_plan,
                            },
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"message": f"Payment failed. kindly retry"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except IntegrityError as e:
            return Response({"error": e.args}, status=status.HTTP_400_BAD_REQUEST)


class UpdateRecurring(UpdateAPIView):
    queryset = SubscriptionPerAgent.objects.all()
    serializer_class = SubPerAgentSerializer
    lookup_field = "reference_code"
    permission_classes = [IsAuthenticated & UserIsAnAgent]


class UpdateChargeType(UpdateAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    lookup_field = "agent_id"
    permission_classes = [IsAuthenticated & UserIsAnAgent]
