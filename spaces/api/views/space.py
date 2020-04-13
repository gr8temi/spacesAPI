from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..models.spaces import Space
from ..serializers.space import SpaceSerializer
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
import os


class Spaces(APIView):
    def get(self, request, format="json"):
        queryset = Space.objects.all()
        serializer = SpaceSerializer(queryset, many=True)
        return Response({"payload": serializer.data, "message": "fetch successful"}, status=status.HTTP_200_OK)
