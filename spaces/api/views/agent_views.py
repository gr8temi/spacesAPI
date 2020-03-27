from rest_framework.views import APIView
from ..models.agent import Agent
from ..models.user import User
from ..serializers.agents_serializers import AgentSerializer
from ..serializers.users_serializer import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated


class AgentList(APIView):
    # permission_classes=[IsAuthenticated,]

    def get(self, request, format=None):
        queryset = Agent.objects.all()
        serializer = AgentSerializer(queryset, many=True)
        return Response(serializer.data)


class AgentDetail(APIView):
    # permission_classes = [IsAuthenticated,]
    def get_object(self, agent_id):
        try:
            return Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            raise Http404

    def get(self, request, agent_id, format=None):
        agent = self.get_object(agent_id)
        serializer = AgentSerializer(agent)
        return Response(serializer.data)

    def put(self, request, agent_id):
        agent = self.get_object(agent_id)
        serializer = AgentSerializer(agent, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, agent_id, format=None):
        agent = self.get_object(agent_id)
        agent.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AgentRegister(APIView):
    # permission_classes = [IsAuthenticated, ]
    def get_object(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        data = request.data
        username = request.POST['username']
        user_id = User.objects.filter(
            username=username).values_list('id', flat=True)
        business_name = data.get('business_name')
        office_address = data.get('office_address')
        validated = data.get('validated')
        agent_data = {
            'business_name': business_name,
            'office_address': office_address,
            'validated': validated,
            'user': user_id.first()
        }

        user_data = {
            'username': username,
            'name': data.get('name'),
            'email': data.get('email'),
            'phone_number': data.get('phone_number'),
            'password': data.get('password'),
            'is_agent':True,
            'is_customer':False,
            # 'token': " "
        }

        if user_id:
            serializer = AgentSerializer(data=agent_data)
            if serializer.is_valid():
                serializer.save()
                # user = self.get_object(user_id.first())
                user = User.objects.get(username=username)
                user.is_agent = True
                # update_user = UserSerializer(user, data=user_data)
                # if user.is_valid():
                user.save(update_fields=['is_agent',])
                return Response(serializer.data, status=status.HTTP_200_OK)
                # return user 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            new_user = UserSerializer(data=user_data)
            if new_user.is_valid():
                new_user.save()
                new_user_id = User.objects.filter(
                    username=username).values_list('id', flat=True)
                agent_data['user'] = new_user_id.first()
                serializer = AgentSerializer(data=agent_data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(new_user.errors, status=status.HTTP_400_BAD_REQUEST)
