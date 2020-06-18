from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated


from ..models.spaces import Space
from ..serializers.space import SpaceSerializer
from ..serializers.availabilty import AvailabilitySerializer
from ..serializers.extra import ExtraSerializer


class CreateSpace(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format="json"):

        data = request.data
        name = data['name']
        space_category= data['space_category']
        existing = Space.objects.filter(name=name, space_category=space_category)

        def save_to_model(field, serializer):
            for i in range(len(field)):
                serialized = serializer(data={**field[i], 'space': name})
                if serialized.is_valid():
                    serialized.save()

        space_data = {
        'name': data['name'],
        'description': data['description'],
        'space_category': data['space_category'],
        'address': data['address'],
        'gmap': data['gmap'],
        'number_of_bookings': data['number_of_bookings'],
        'capacity': data['capacity'],
        'amount': data['amount'],
        'agent': data['agent'],
        'duration': data['duration'],
        'images': data['images'],
        'videos': data['videos'],
        'amenities': data['amenities'],
        'carspace': data['carspace'],
        'rules': data['rules'],
        'cancellation_rules': data['cancellation_rules']
        }

        spaceDataSerializer = SpaceSerializer(data=space_data)
        availability = data['availability']
        extras = data['extras']

        if bool(existing):
            return Response({"message": f"Space with name {name} already exists in this category"}, status=status.HTTP_400_BAD_REQUEST)

        elif spaceDataSerializer.is_valid():
            spaceDataSerializer.save()

            save_to_model(availability, AvailabilitySerializer)
            save_to_model(extras, ExtraSerializer)

            name = spaceDataSerializer.data["name"]
            return Response({"payload":spaceDataSerializer.data, "message":f"{name} was created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"message":"Check your input, some fields might be missing","error": spaceDataSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)       

