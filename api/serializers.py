from rest_framework import serializers
from .models import Project, Task, CustomUser, PointsProject, Invitation
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']

class CustomUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = CustomUser
        fields = ['user', 'is_professor']

class ProjectSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(required=False)
    collaborators = CustomUserSerializer(required=False, many=True)
    teachers = CustomUserSerializer(required=False, many=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'collaborators', 'teachers', 'creator']

class TaskSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(required=False)
    collaborators = CustomUserSerializer(required=False, many=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'description','start_date', 'finish_date',
                   'story_points', 'state', 'estimated_hours', 'total_hours',
                   'creator', 'collaborators']

class PointsProjectSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.user.username', read_only=False)

    class Meta:
        model = PointsProject
        fields = ['username', 'project_id', 'points']

class InvitationSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(required=False)
    receiver = CustomUserSerializer(required=False)

    class Meta:
        model = Invitation
        field = ['sender', 'receiver', 'state']
