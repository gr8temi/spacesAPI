from rest_framework.views import APIView
from ..models.spaces import Space
from ..serializers.space_serializer import SpaceSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class SpaceDetail(APIView):

    def get_space(self, space_id):
        try:
            return Space.object.get(id=space_id)
        except Space.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        queryset = Space.objects.all()
        serializer = SpaceSerializer(queryset, many=True)
        return Response(serializer.data)

    def delete(self, request, space_id, format=None):
        space = self.get_space(space_id)
        space.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SpaceEdit(APIView):
    def get_space(self, space_id):
        try:
            return Space.object.get(id=space_id)
        except Space.DoesNotExist:
            raise Http404


    def put(self, request, space_id):
        space = self.get_space(space_id)
        serializer = SpaceSerializer(space, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

