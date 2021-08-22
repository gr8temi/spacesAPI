import uuid
import calendar
from datetime import datetime, timedelta
import pytz

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
from ..serializers.order import OrdersFetchSerializer
from ..serializers.rating import RatingSerializer


class Analytics(APIView):

    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def get(self, request, agent_id):
        try:
            agent = Agent.objects.get(agent_id=uuid.UUID(agent_id))
        except:
            return Response({"message": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)

        today = datetime.today()
        month_beginning = datetime(today.year, today.month, 1)
        two_months_ago = pytz.utc.localize(
            month_beginning) - timedelta(days=30)
        three_months_ago = pytz.utc.localize(
            month_beginning) - timedelta(days=60)
        a_month_ago = pytz.utc.localize(month_beginning)
        a_week_ago = timezone.now() - timedelta(days=7)

        agent_spaces = Space.objects.filter(agent=agent)
        booking_orders = Order.objects.filter(
            order_type__order_type="booking", status="booked", offline_booking=False, space__agent=agent)
        reservation_orders = Order.objects.filter(
            order_type__order_type="reservation", space__agent=agent)
        least_used_space = SpaceSerializer(min(
            agent_spaces, key=lambda space: space.number_of_bookings)).data if len(agent_spaces)>0 else None  # least used space
        most_used_space = SpaceSerializer(max(
            agent_spaces, key=lambda space: space.number_of_bookings)).data if len(agent_spaces)>0 else None  # Most used space

        no_of_spaces = agent_spaces.count()
        no_of_bookings = booking_orders.count()
        no_of_reservations = reservation_orders.count()

        spaces_with_space_type = list(agent_spaces.values(
            "space_type__space_type").annotate(Count("space_type")))

        weekly_bookings = booking_orders.filter(
            order_time__gte=a_week_ago).count()
        monthly_bookings = booking_orders.filter(
            order_time__gte=a_month_ago).count()

        weekly_reservations = reservation_orders.filter(
            order_time__gte=a_week_ago).count()
        monthly_reservations = reservation_orders.filter(
            order_time__gte=a_month_ago).count()

        spaces_with_its_respective_booking = Space.objects.prefetch_related(
            Prefetch("order", queryset=booking_orders))

        agent_total_amount_made = Order.objects.filter(space__agent=agent,order_type__order_type="booking",offline_booking=False, status="booked").aggregate(
            amount_sum=Sum(Cast("amount", FloatField())))["amount_sum"]
        if agent_total_amount_made:
            amount_made_after_deduction = agent_total_amount_made
        else:
            amount_made_after_deduction = 0.0

        

        agent_ratings = Rating.objects.filter(space__agent=agent)
        ratings_data = RatingSerializer(agent_ratings, many=True).data
        if agent_ratings.count() > 0:
            good_review_percentage = (agent_ratings.filter(
                ratings__gte=3).count() / agent_ratings.count()) * 100
            bad_review_percentage = (agent_ratings.filter(
                ratings__lt=3).count() / agent_ratings.count()) * 100
        else:
            good_review_percentage = 0
            bad_review_percentage = 0

        space_analysis_list = []

        for space in spaces_with_its_respective_booking:

            if space.agent == agent:

                two_months_ago_booking = space.order.filter(
                    order_time__gte=two_months_ago, order_time__lte=a_month_ago).count()
                three_months_ago_booking = space.order.filter(
                    order_time__gte=three_months_ago, order_time__lte=two_months_ago).count()

                space_analysis = {
                    "space_name": space.name,
                    "one_month": [{"year":datetime.now().year,"month": calendar.month_abbr[datetime.now().month], "value": space.order.filter(order_time__gte=a_month_ago, order_time__lte=timezone.now()).count()}],
                    "two_month": [{"year": two_months_ago.year, "month": calendar.month_abbr[two_months_ago.month], "value":two_months_ago_booking}, {"year": datetime.now().year, "month": calendar.month_abbr[datetime.now().month], "value":space.order.filter(
                        order_time__gte=a_month_ago, order_time__lte=timezone.now()).count()}],
                    "three_month": [{"year": three_months_ago.year, "month": calendar.month_abbr[three_months_ago.month], "value":three_months_ago_booking}, {"year": two_months_ago.year, "month": calendar.month_abbr[two_months_ago.month], "value":two_months_ago_booking}, {"year": datetime.now().year, "month": calendar.month_abbr[datetime.now().month], "value":space.order.filter(
                        order_time__gte=a_month_ago, order_time__lte=timezone.now()).count()}],
                    "weekly_booking": space.order.filter(order_time__gte=a_week_ago).count(),
                    "bookings": OrdersFetchSerializer(space.order.all(), many=True).data,
                }
                space_analysis_list.append(space_analysis)
        data = {
            "weekly_bookings": weekly_bookings,
            "monthly_bookings": monthly_bookings,
            "weekly_reservations": weekly_reservations,
            "monthly_reservations": monthly_reservations,
            "number_of_spaces": no_of_spaces,
            "number_of_bookings": no_of_bookings,
            "number_of_reservations": no_of_reservations,
            "least_used_space": least_used_space,
            "most_used_space": most_used_space,
            "space_analysis": space_analysis_list,
            "spaces_with_space_type": spaces_with_space_type,
            "agent_total_amount_made": agent_total_amount_made,
            "amount_made_after_deduction": amount_made_after_deduction,
            "ratings_data": ratings_data,
            "good_review_percentage": good_review_percentage,
            "bad_review_percentage": bad_review_percentage,
        }
        return Response({"message": "Analysis returned successfully", "payload": data}, status=status.HTTP_200_OK)


class RevenueAnalytics(APIView):
    permission_classes = [IsAuthenticated & UserIsAnAgent]

    def get(self, request, agent_id):
        try:
            agent = Agent.objects.get(agent_id=uuid.UUID(agent_id))
        except:
            return Response({"message": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)
        
        str_start_date = request.GET.get('start_date')
        start_date = datetime.fromisoformat(str_start_date.replace('Z', '+00:00'))

        str_end_date = request.GET.get('end_date')
        end_date = datetime.fromisoformat(str_end_date.replace('Z', '+00:00'))

        revenues_within_range = list(Order.objects.filter(space__agent__agent_id=agent_id, order_type__order_type="booking", order_time__range=[start_date, end_date]).values("amount"))
        sum_revenues_within_range = 0

        for revenue in revenues_within_range:
            sum_revenues_within_range += int(revenue['amount'])

        total_revenue_within_range = sum_revenues_within_range - (0.08 * sum_revenues_within_range)

        return Response({"message": "Total Revenue returned successfully", "total_revenue": total_revenue_within_range}, status=status.HTTP_200_OK)
