from rest_framework import serializers
from ..models.user import User
import bcrypt
from rest_framework_simplejwt.models import TokenUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ('id', 'name', 'email', 'username', 'password')
        fields = '__all__'
        

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password').encode('utf-8')
        password = bcrypt.hashpw(password, bcrypt.gensalt())
        validated_data['password'] = password
        user = User.objects.create(**validated_data)
        return user