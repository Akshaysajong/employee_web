from calendar import c
from rest_framework import serializers
from accounts.models import CustomUser
from .forms import CustomUserCreationForm, CustomUserLogin
from django.contrib.auth import authenticate
from .models import Task
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        form = CustomUserCreationForm(validated_data)

        if not form.is_valid():
            # Convert Django form errors to DRF validation errors
            raise serializers.ValidationError(form.errors)

        return form.save()

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if not user.is_active:
                raise serializers.ValidationError("User is deactivated.")
            return user
        else:
            raise serializers.ValidationError("Invalid credentials.")
       

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'completed', 'created_at', 'updated_at', 'user']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']