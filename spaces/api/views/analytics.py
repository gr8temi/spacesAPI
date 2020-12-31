import uuid
from datetime import timedelta

from django.db.models import Sum, Count, FloatField
from django.db.models.functions import Cast
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from ..models.spaces import Space
from ..models.order import Order
from ..models.agent import Agent
from ..models.ratings import Rating
from ..permissions.is_agent_permission import UserIsAnAgent
from ..serializers.space import SpaceSerializer
from ..serializers.order import  OrdersFetchSerializer
from ..serializers.rating import RatingSerializer

class Analytics(APIView):

    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def get(self, request, agent_id):
        try:
            agent = Agent.objects.get(agent_id=uuid.UUID(agent_id))
        except:
            return Response({"message":"Agent not found"}, status=status.HTTP_404_NOT_FOUND)

        a_month_ago = timezone.now() - timedelta(days=30)
        a_week_ago = timezone.now() - timedelta(days=7)
        
        agent_spaces = Space.objects.filter(agent=agent)
        booking_orders = Order.objects.filter(order_type__order_type="booking")
        reservation_orders = Order.objects.filter(order_type__order_type="reservation")

        least_used_space = SpaceSerializer(min(agent_spaces, key = lambda space: space.number_of_bookings)).data # least used space
        most_used_space = SpaceSerializer(max(agent_spaces, key = lambda space: space.number_of_bookings)).data # Most used space
        
        no_of_spaces = agent_spaces.count()
        no_of_bookings = booking_orders.count()
        no_of_reservations = reservation_orders.count()

        spaces_with_space_type = list(agent_spaces.values("space_type__space_type").annotate(Count("space_type")))

        weekly_bookings = booking_orders.filter(order_time__gte = a_week_ago).count()
        monthly_bookings = booking_orders.filter(order_time__gte = a_month_ago).count()

        weekly_reservations = reservation_orders.filter(order_time__gte = a_week_ago).count()
        monthly_reservations = reservation_orders.filter(order_time__gte = a_month_ago).count()

        spaces_with_its_respective_booking = Space.objects.prefetch_related(Prefetch("order", queryset=booking_orders))

        agent_total_amount_made = Order.objects.filter(space__agent=agent).aggregate(amount_sum=Sum(Cast("amount",FloatField())))["amount_sum"]
        amount_made_after_deduction = agent_total_amount_made * 0.92

        agent_ratings = Rating.objects.filter(space__agent=agent)
        ratings_data = RatingSerializer(agent_ratings, many=True).data
        if agent_ratings.count() > 0:
            good_review_percentage = (agent_ratings.filter(ratings__gte=3).count() / agent_ratings.count()) * 100
            bad_review_percentage = (agent_ratings.filter(ratings__lt=3).count() / agent_ratings.count()) * 100
        else:
            good_review_percentage = 0
            bad_review_percentage = 0

        space_analysis_list = []

        for space in spaces_with_its_respective_booking:
            
            if space.agent == agent:
                space_analysis = {
                    "space_name": space.name,
                    "monthly_booking": space.order.filter(order_time__gte = a_month_ago).count(),
                    "weekly_booking": space.order.filter(order_time__gte = a_week_ago).count(),
                    "bookings": OrdersFetchSerializer(space.order.all(), many=True).data,
                    
                }
            space_analysis_list.append(space_analysis)
        data = {
            "weekly_bookings": weekly_bookings,
            "monthly_bookings": monthly_bookings,
            "weekly_reservations": weekly_reservations,
            "monthly_reservations": monthly_reservations,
            "number_of_spaces":no_of_spaces,
            "number_of_bookings": no_of_bookings,
            "number_of_reservations": no_of_reservations,
            "least_used_space": least_used_space,
            "most_used_space": most_used_space,
            "space_analysis": space_analysis_list,
            "spaces_with_space_type":spaces_with_space_type,
            "agent_total_amount_made":agent_total_amount_made,
            "amount_made_after_deduction":amount_made_after_deduction,
            "ratings_data":ratings_data,
            "good_review_percentage":good_review_percentage,
            "bad_review_percentage":bad_review_percentage,
        }
        return Response({"message": "Analysis returned successfully", "payload":data}, status=status.HTTP_200_OK)





