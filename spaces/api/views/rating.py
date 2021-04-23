import uuid
from django.db.models import Avg

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from api.models.ratings import Rating
from api.models.spaces import Space
from api.serializers.rating import RatingSerializer, RatingDetailSerializer


class RateASpace(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self,request):
        data = {}
        data["user"] =  request.data.get("name")  
        data["ratings"] = float(request.data.get("rating"))
        data["comment"] = request.data.get("message")
        data["space"] = request.data.get("space")
        data["order_id"] = request.data.get("booking")
        try:
            space = Space.objects.get(space_id=uuid.UUID(data["space"]))
        except:
            return Response({"message": "Space does not exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RatingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            rating_average = Rating.objects.filter(
                space=space).aggregate(rating=Avg("ratings"))
            space.ratings = rating_average["rating"]
            space.save()
            return Response({"message": "rating successfully done", "payload":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Error creating a rating", "payload":serializer.custom_full_errors}, status=status.HTTP_400_BAD_REQUEST)


class SpaceRating(APIView):
    
    def get(self,request,space_id):

        ratings = Rating.objects.filter(space__space_id=uuid.UUID(space_id))

        space_ratings = RatingDetailSerializer(ratings, many=True).data

        return Response({"message": "Ratings fetched", "payload": space_ratings}, status=status.HTTP_200_OK)
class AgentRating(APIView):

    def get(self,request,agent_id):

        ratings = Rating.objects.filter(space__agent__agent_id=uuid.UUID(agent_id))

        space_ratings = RatingDetailSerializer(ratings, many=True).data

        return Response({"message": "Ratings fetched", "payload": space_ratings}, status=status.HTTP_200_OK)


            

        


