from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class Spaces(APIView):
    def get(self,request):
        return


class SpacesDetail(APIView):
    def get(self,request,spaceId):
        return