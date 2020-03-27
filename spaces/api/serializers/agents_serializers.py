from rest_framework import serializers
from ..models.agent import Agent
from ..models.user import User
from .users_serializer import UserSerializer


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'

    # def create(self, validated_data):
    #     business_name = validated_data.pop('business_name')
    #     office_address = validated_data.pop('office_address')
    #     validated = validated_data.pop('validated')
    #     user_id = validated_data.pop('user')

    #     agent_data = {
    #         'business_name': business_name,
    #         'office_address': office_address,
    #         'validated' : validated
    #     }

        # username = validated_data.get('username')
        
        # user = User.objects.get(username=username)
        # # user = UserSerializer(user)
        # # if not user.is_agent:
        # # agent_data['user'] = user.id
        # # user.is_agent = True
        # return Agent.objects.create(**agent_data)
        # else:
        #     user = User.objects.create(**validated_data)
        #     user.save()
        #     agent_data['user'] = user.id
        #     user.is_agent = True
        #     return Agent.objects.create(**validated_data)

    #     serialize = UserSerializer(user)
    #     return serialize.data.email
    #     # try:
            # return User.objects.get(username=validated_data['username'])
            # user = User.objects.get(username=validated_data['username'])
            # if user.email == validated_data['email']:
            #     if user.is_agent:
            #         return f"{user.username} is already an agent"
            #     else:
            #         agent = Agent.objects.create(**validated_data)
                    #
        # except User.DoesNotExist():
            # return "Implementation in progress"

      
