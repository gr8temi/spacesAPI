from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.core.mail import send_mail


class PaystackHooks(APIView):
    def post(self, request):
        data = request.body
        event = data.event
        print({"event": event, "data": data})
        send_mail(
            "Subject here",
            f"Here is the message.{event}",
            "damstemii@gmail.com",
            ["gr8temi@gmail.com"],
            fail_silently=False,
        )
        return Response({"message": "done"}, status=status.HTTP_200_OK)
