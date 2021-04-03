from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..models.spaces_category import SpaceCategory
from ..serializers.space_category import SpaceSerializer
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
import os
from rest_framework.permissions import AllowAny


class SpacesCategory(APIView):
    permission_classes = [AllowAny]

    def get_category(self, space_category_id):
        try:
            category = get_object_or_404(
                SpaceCategory, category_id=space_category_id)
        except Exception as err:
            return False

    def get(self, request):
        categories = SpaceCategory.objects.all()
        if categories:
            serializer = SpaceSerializer(categories, many=True)
            return Response({"payload": serializer.data, "message": "fetch successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "fetch was not successful"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format="json"):

        data = request.data
        name = data.get("space_category")

        if SpaceCategory.objects.filter(space_category=name):
            return Response({"message": "Category already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SpaceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            type_of_space = serializer.data.get("space_category")
            return Response({"payload": serializer.data, "message": f"category {type_of_space.upper()} created"}, status=status.HTTP_201_CREATED)
