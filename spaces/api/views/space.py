from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..models.spaces import Space
from ..models.order import Order
from ..models.availabilities import Availability
from ..models.extras import Extra
from ..serializers.space import SpaceSerializer
from ..serializers.order import OrderSerializer
from ..serializers.availabilty import AvailabilitySerializer
from ..serializers.extra import ExtraSerializer
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
import os
from rest_framework.generics import UpdateAPIView, DestroyAPIView
from ..permissions.is_agent_permission import UserIsAnAgent


class Spaces(APIView):
    def get(self, request, format="json"):
        queryset = Space.objects.all()
        serializer = SpaceSerializer(queryset, many=True)
        return Response({"payload": serializer.data, "message": "fetch successful"}, status=status.HTTP_200_OK)


class SingleSpace(APIView):
    def get_space(self, space_id):

        try:
            return Space.objects.get(space_id=space_id)
        except:
            return False

    def get_availability(self, space):
        try:
            return Availability.objects.filter(space=space)
        except Exception as err:

            return False

    def get_extra(self, space):
        try:

            return Extra.objects.filter(space=space)
        except Exception as err:

            return False

    def get_booked(self, space_id):
        try:

            return Order.objects.filter(space=space_id)
        except Exception as err:

            return False

    def get(self, request, space_id):
        space = self.get_space(space_id)

        if space:
            availability = self.get_availability(space)
            extras = self.get_extra(space)

            booked = self.get_booked(space_id)

            space_serializer = SpaceSerializer(space)
            extra_serializer = ExtraSerializer(extras, many=True)
            availability_serializer = AvailabilitySerializer(
                availability, many=True)
            bookedSerializer = OrderSerializer(booked, many=True)
            return Response({"message": "Space fetched successfully", "payload": {**space_serializer.data, "availability": availability_serializer.data, "extras": extra_serializer.data, "booked_date": bookedSerializer.data}}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Error fetching space, Space does not Exist"}, status=status.HTTP_400_BAD_REQUEST)


class EditSpace(UpdateAPIView):

    queryset = Space.objects.all()
    serializer_class = SpaceSerializer
    lookup_field = 'space_id'
    permission_classes = [IsAuthenticated & UserIsAnAgent]


class DeleteSpace(DestroyAPIView):
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer
    lookup_field = 'space_id'
    permission_classes = [IsAuthenticated & UserIsAnAgent]
