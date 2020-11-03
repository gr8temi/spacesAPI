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
            if space.city is None and space.gmap:
                geolocator = GoogleV3(
                    api_key="AIzaSyBljfjq7_UASNByc268yuYTtjGIO22GFv8")
                print(space.gmap)
                location = geolocator.reverse(space.gmap.values())
                address_components = location.raw["address_components"]
                print(address_components)
                for component in address_components:
                    if "locality" in component["types"] or "postal_town" in component["types"]:
                        cities.append(component["short_name"])
            else:
                cities.append(space.city)

        return Response({"message": "cities fetched successfully", "payload": set(cities)}, status=status.HTTP_200_OK)
