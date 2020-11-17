import uuid
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated


from ..models.spaces import Space
from ..models.agent import Agent
from ..serializers.space import SpaceSerializer
from ..serializers.availabilty import AvailabilitySerializer
from ..serializers.extra import ExtraSerializer

from ..signals import subscriber
from ..consumers.channel_layers import notification_creator


class CreateSpace(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format="json"):

        data = request.data

        name = data.get('name')
        space_type = data.get('space_type')
        existing = Space.objects.filter(
            name=name, space_type=space_type)

        def save_to_model(space_id, field, serializer):
            for i in range(len(field)):
                serialized = serializer(data={**field[i], 'space': space_id})
                if serialized.is_valid():
                    serialized.save()

        space_data = {
            'name': data.get('name'),
            'description': data.get('description'),
            # data.get('space_type'),
            # "2ce6293c-f8cf-41d4-9d77-bed08a9d74e5",
            'space_type': data.get('space_type'),
            'address': data.get('address'),
            'gmap': data.get('gmap'),
            'capacity': data.get('capacity'),
            'state': data.get('state'),
            'city': data.get('city'),
            'amount': data.get('amount'),
            'agent': data.get('agent'),
            'duration': data.get('duration'),
            'images': data.get('images'),
            # 'videos': data.get('videos'),
            'amenities': data.get('amenities'),
            'rules': data.get('rules'),
            'cancellation_rules': data.get('cancellation_rules')
        }
        user_id = Agent.objects.get(agent_id=uuid.UUID(
            data.get("agent"))).user.user_id  # TODO: Catch error if it fails
        spaceDataSerializer = SpaceSerializer(data=space_data)
        availability = data['availability']
        extras = data.get('extras')

        if bool(existing):
            return Response({"message": f"Space with name {name} already exists in this category"}, status=status.HTTP_400_BAD_REQUEST)

        elif spaceDataSerializer.is_valid():
            spaceDataSerializer.save()
            space_name = spaceDataSerializer.data.get("name")
            try:
                space_id = Space.objects.get(name=space_name).space_id
            except:
                return Response({"message": "Does Not Exist"}, status=status.HTTP_404_NOT_FOUND)
            save_to_model(f"{space_id}", availability, AvailabilitySerializer)
            save_to_model(f"{space_id}", extras, ExtraSerializer)

            name = spaceDataSerializer.data.get("name")
            subscriber.connect(notification_creator)
            subscriber.send(sender=self.__class__,
                            data={"name": space_id, "user_id": f"{user_id}", "notification": f"{space_id} was successfully created"})

            return Response({"payload": spaceDataSerializer.data, "message": f"{name} was created successfully"}, status=status.HTTP_201_CREATED)

        return Response({"message": "Check your input, some fields might be missing", "error": spaceDataSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)
