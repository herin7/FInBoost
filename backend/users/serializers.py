# users/serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_picture', 'role','password')
    extra_kwargs = {"password" : {"write_only" : True}}
    def create( self, validated_data): 
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user
