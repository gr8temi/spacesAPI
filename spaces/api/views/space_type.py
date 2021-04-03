import uuid
from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..models.space_type import SpaceType
from ..serializers.space_type import SpaceTypeSerializer, SpaceTypeSerializerDetails
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
import os
from rest_framework.permissions import AllowAny


class SpaceTypeView(APIView):
    permission_classes = [AllowAny]

    def get_category(self, space_type_id):
        try:
            category = get_object_or_404(
                SpaceType, space_type_id=space_type_id)
        except Exception as err:
            return False

    def get(self, request):
        space_type = SpaceType.objects.all()

        serializer = SpaceTypeSerializerDetails(space_type, many=True)
        return Response({"payload": serializer.data, "message": "fetch successful"}, status=status.HTTP_200_OK)

    def post(self, request, format="json"):

        data = request.data
        name = data.get("space_type")
        category = data.get("space_category")
        if SpaceType.objects.filter(space_type=name, space_category__category_id=uuid.UUID(category)):
            return Response({"message": "Space type already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SpaceTypeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            type_of_space = serializer.data.get("space_type")
            return Response({"payload": serializer.data, "message": f"Space Type {type_of_space.upper()} created"}, status=status.HTTP_201_CREATED)

class SpaceTypeDetail(APIView):
    def get(self, request, space_type_id):

        try:
            space_type = SpaceType.objects.get(space_type_id=uuid.UUID(space_type_id))
        except SpaceType.DoesNotExist:
            return Response({"message": "Spacetype Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SpaceTypeSerializerDetails(space_type)

        return Response({"message":"SpaceType Fetch Successful", "payload":serializer.data}, status=status.HTTP_200_OK)


class SpaceTypeByCategory(APIView):
    def get(self, request, category_id):
        space_types = SpaceType.objects.filter(
                space_category__category_id=uuid.UUID(category_id))
        serializer = SpaceTypeSerializerDetails(space_types, many=True)

        return Response({"message":"SpaceType Fetch Successful", "payload":serializer.data}, status=status.HTTP_200_OK)
