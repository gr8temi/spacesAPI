from rest_framework.views import APIView
from ..serializers.favourite import FavouriteSerializer, FavouriteSpaceSerializer
from rest_framework.response import Response
from rest_framework import status
from ..models.favourite import Favourite
from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import IsAuthenticated


class AddFavorite(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = FavouriteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Space added succesfully to Favorites"}, status=status.HTTP_201_CREATED)
        return Response(serializer.custom_full_errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        queryset = Favourite.objects.all()
        serializer = FavouriteSerializer(queryset, many=True)
        return Response({"message": "Favourites fetched successfully", "payload": serializer.data}, status=status.HTTP_200_OK)


class FetchUserFavourites(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        queryset = Favourite.objects.filter(user__user_id=user_id)
        serializer = FavouriteSpaceSerializer(queryset, many=True)
        return Response({"message": "Favourites fetched successfully", "payload": serializer.data}, status=status.HTTP_200_OK)


class DeleteFavourite(DestroyAPIView):

    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
    lookup_field = 'favorite_id'
    permission_classes = [IsAuthenticated]
