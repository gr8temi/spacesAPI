from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

class PaystackHooks(APIView):

    def post(self, request):
        data = request.body
        event = data.event
        print({"event":event,"data":data})
        return Response({"message":"done"}, status=status.HTTP_200_OK)