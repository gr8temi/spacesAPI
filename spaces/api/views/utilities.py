from rest_framework.views import APIView
from rest_framework.response import Response
from geopy.geocoders import GoogleV3
from ..models.spaces import Space
from rest_framework import status


class SpaceLocation(APIView):

    def get_queryset(self):
        return Space.objects.all()

    def get(self, request):
        all_spaces = self.get_queryset()
        cities = []
        for space in all_spaces:
            if space.city is not None:
                cities.append(space.city)

        return Response({"message": "cities fetched successfully", "payload": set(cities)}, status=status.HTTP_200_OK)
