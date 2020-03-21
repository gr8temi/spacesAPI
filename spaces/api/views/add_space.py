from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated


from ..models.spaces import Space
from ..serializers.space import SpaceSerializer


class CreateSpace(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format="json"):
        serializer = SpaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)       

