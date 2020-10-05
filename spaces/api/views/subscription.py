from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..permissions.is_agent_permission import UserIsAnAgent
from ..helper.helper import reference_code
from ..models.subscription import Subscription, SubscriptionPerAgent, BillingHistory
from ..serializers.subscription import SubscriptionSerializer, SubPerAgentSerializer, BillHistSerializer
from rest_framework.generics import UpdateAPIView, DestroyAPIView


from spaces.paystack import paystack

class Subscribe(APIView):

    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def post(self, request):
        data = request.data
        subscription_type = data.get("subscription_type")
        agent = data.get("agent")
        recurring = data.get("recurring")
        reference = reference_code()
        try:
            subscription = Subscription.objects.get(
                subscription_type=subscription_type)
        except Subscription.DoesNotExist:
            return Response({"message": "Subscription type selected does not exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubPerAgentSerializer(data={
            "subscription": f"{subscription.subscription_id}",
            "recurring": recurring,
            "reference_code": reference,
            "agent": agent
        })

        if serializer.is_valid():
            serializer.save()

            return Response({"message": "Subscription created successfully expecting update on payment", "payload": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Error processing subscription", "payload": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        queryset = Subscription.objects.all()
        serializer = SubscriptionSerializer(queryset, many=True)

        return Response({"message": "Subscriptions Fetched", "payload": serializer.data}, status=status.HTTP_200_OK)


class SubscribeActions(APIView):

    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def put(self, request, reference_code):
        verified_payment = paystack.transaction.verify(
            reference=reference_code)
        try:
            agent_subscription = SubscriptionPerAgent.objects.get(
                reference_code=reference_code)
        except SubscriptionPerAgent.DoesNotExist:
            return Response({"message", "Subscription does not exist"}, status=status.HTTP_404_NOT_FOUND)

        previous_paid_at = agent_subscription.paid_at

        if previous_paid_at >= datetime.strptime(
                verified_payment["data"]["paid_at"].split(".")[0], "%Y-%m-%dT%H:%M:%S") and agent_subscription.paid==True:
            return Response({"message": f"Payment made is already active and expires {agent_subscription.next_due_date}"})

        if previous_paid_at >= datetime.strptime(
            verified_payment["data"]["paid_at"].split(".")[0], "%Y-%m-%dT%H:%M:%S") and agent_subscription.paid == False:
            return Response({"message": f"This payment has either expired at this date {agent_subscription.next_due_date}"})
        
        if verified_payment["status"]:
            authorization_code = verified_payment["data"]["authorization"]["authorization_code"]
            subscription_type = agent_subscription.subscription_type()
            start_time = datetime.now()

            if subscription_type == "monthly":
                due_date = SubscriptionPerAgent.objects.monthly_subscription(
                    start_time)
            elif subscription_type == "quarterly":
                due_date = SubscriptionPerAgent.objects.quarterly_subscription(
                    start_time)
            elif subscription_type == "bi-annually":
                due_date = SubscriptionPerAgent.objects.bi_annual_subscription(
                    start_time)
            elif subscription_type == "yearly":
                due_date = SubscriptionPerAgent.objects.annual_subscription(
                    start_time)
            elif subscription_type == "per minute":
                due_date = SubscriptionPerAgent.objects.minute_subscription(
                    start_time)
            else:
                return Response({"message", "Subscription type selected does not exist"}, status=status.HTTP_404_NOT_FOUND)

            agent_subscription.next_due_date = due_date
            agent_subscription.paid = True
            agent_subscription.paid_at = datetime.strptime(
                verified_payment["data"]["paid_at"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
            agent_subscription.authorization_code = authorization_code
            agent_subscription.amount = verified_payment["data"]["amount"]/100
            agent_subscription.save()

            return Response({"message": f"Subscription successful. Next due date is {due_date}", "payload": verified_payment}, status=status.HTTP_200_OK)
        else:
            return Response({"message": f"Payment failed. kindly retry"}, status=status.HTTP_400_BAD_REQUEST)


class UpdateRecurring(UpdateAPIView):
    queryset = SubscriptionPerAgent.objects.all()
    serializer_class = SubPerAgentSerializer
    lookup_field = 'reference_code'
    permission_classes = [IsAuthenticated & UserIsAnAgent]
