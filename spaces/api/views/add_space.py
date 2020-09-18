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

        name = data['name']
        space_type = data['space_type']
        existing = Space.objects.filter(
            name=name, space_type=space_type)

        def save_to_model(space_id, field, serializer):
            for i in range(len(field)):
                serialized = serializer(data={**field[i], 'space': space_id})
                if serialized.is_valid():
                    serialized.save()

        space_data = {
            'name': data['name'],
            'description': data['description'],
            # data['space_type'],
            # "2ce6293c-f8cf-41d4-9d77-bed08a9d74e5",
            'space_type': data['space_type'],
            'address': data['address'],
            'gmap': data['gmap'],
            'capacity': data['capacity'],
            'amount': data['amount'],
            'agent': data['agent'],
            'duration': data['duration'],
            'images': data['images'],
            # 'videos': data['videos'],
            'amenities': data['amenities'],
            'rules': data['rules'],
            'cancellation_rules': data['cancellation_rules']
        }
        user_id = Agent.objects.get(agent_id= uuid.UUID(data["agent"])).user.user_id #TODO: Catch error if it fails
        spaceDataSerializer = SpaceSerializer(data=space_data)
        availability = data['availability']
        extras = data['extras']

        if bool(existing):
            return Response({"message": f"Space with name {name} already exists in this category"}, status=status.HTTP_400_BAD_REQUEST)

        elif spaceDataSerializer.is_valid():
            spaceDataSerializer.save()
            space_id = spaceDataSerializer.data["name"]
            save_to_model(space_id, availability, AvailabilitySerializer)
            save_to_model(space_id, extras, ExtraSerializer)

            name = spaceDataSerializer.data["name"]
            subscriber.connect(notification_creator)
            subscriber.send(sender=self.__class__,
                            data={"name":space_id,"user_id":f"{user_id}", "notification":f"{space_id} was successfully created"})

            return Response({"payload": spaceDataSerializer.data, "message": f"{name} was created successfully"}, status=status.HTTP_201_CREATED)

        return Response({"message": "Check your input, some fields might be missing", "error": spaceDataSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)
