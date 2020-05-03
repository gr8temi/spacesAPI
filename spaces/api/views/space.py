from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..models.spaces import Space
from ..models.order import Order
from ..serializers.space import SpaceSerializer
from datetime import date, timedelta, datetime
import os


class Spaces(APIView):
    def get(self, request, format="json"):
        queryset = Space.objects.all()
        serializer = SpaceSerializer(queryset, many=True)
        return Response({"payload": serializer.data, "message": "fetch successful"}, status=status.HTTP_200_OK)


class SpaceDetail(APIView):
    def get_object(self, space_id):
        try:
            return Space.objects.get(space_id=space_id)
        except Space.DoesNotExist:
            return False

    def get(self, request, space_id,):

        space = self.get_object(space_id)
        try:
            ordered = Order.objects.filter(space__space_id=space.space_id)
        except:
            ordered = False
        serializer = SpaceSerializer(space)
        if ordered:

            bookings = [{"start": order.usage_start_date, "end": order.usage_end_date}
                        for order in ordered if str(order.order_type) == "booking"]
            reservations = [{"start": order.usage_start_date, "end": order.usage_end_date, "expires": order.order_time+timedelta(seconds=21600)}
                            for order in ordered if str(order.order_type) == "reservation"]

            return Response({"message": "Space fetched successfully", "payload": {
                **serializer.data,
                "bookings": bookings,
                "reservations": reservations
            }}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Space fetched successfully", "payload": {
                **serializer.data,
            }}, status=status.HTTP_200_OK)

