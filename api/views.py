from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Project, Task
from .serializers import UserSerializer, ProjectSerializer, TaskSerializer
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404


class ProjectsView(APIView):
     permission_classes = (IsAuthenticated, )
     def get(self, request, format=None):
          user = CustomUser.objects.get(user=request.user)
          projects = Project.objects.filter(Q(creator=user) | Q(collaborators__in=[user])).all()
          serializer = ProjectSerializer(projects, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)

     def post(self, request, format=None):
          serializer = ProjectSerializer(data=request.data)
          user = CustomUser.objects.get(user=request.user)
          if serializer.is_valid():
               proj = Project(creator=user, name=serializer.validated_data.get('name'), description=serializer.validated_data.get('description'))
               proj.save()
               proj.collaborators.add(user)
               proj.save()
               return Response(serializer.data, status=status.HTTP_201_CREATED)
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
class ProjectCollaboratorsView(APIView):
    def put(self, request, pk, format=None):
        try:
            project = Project.objects.get(pk=pk)
            user = CustomUser.objects.get(user=request.user)
            project.collaborators.add(user)
            project.save()
            serializer = ProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProjectTeachersView(APIView):
    def put(self, request, pk, format=None):
        try:
            project = Project.objects.get(pk=pk)
            user = CustomUser.objects.get(user=request.user)
            if user.is_professor:
               project.teachers.add(user)
               project.save()
               serializer = ProjectSerializer(project)
               return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"message": "You can only add a teacher to the observers"}, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class TasksView(APIView):
     def get(self, request, pk, format=None):
          proj = get_object_or_404(Project, pk=pk)
          user = CustomUser.objects.get(user=request.user)
          if user not in proj.collaborators.all() and user not in proj.teachers.all():
               return Response({"message": "Can't see tasks if you are not a collaborator!"}, status=status.HTTP_400_BAD_REQUEST)
          tasks = Task.objects.filter(project=proj).all()
          serializer = TaskSerializer(tasks, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)

     def post(self, request, pk, format=None):
          proj = get_object_or_404(Project, pk=pk)
          user = CustomUser.objects.get(user=request.user)
          if user in proj.collaborators.all():
               serializer = TaskSerializer(data=request.data)
               if serializer.is_valid():
                    task = serializer.save()
                    proj = get_object_or_404(Project, pk=pk)
                    user = CustomUser.objects.get(user=request.user)
                    task.creator = user
                    task.project = proj
                    task.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
               return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
          return Response({"message": "Can't add a task if you are not a collaborator!"}, status=status.HTTP_400_BAD_REQUEST)
     
     def put(self, request, pk, format=None):
          task = get_object_or_404(Task, pk=pk)
          user = CustomUser.objects.get(user=request.user)
          if user not in task.project.collaborators.all():
               return Response({"message": "Can't change a task if you are not a collaborator!"}, status=status.HTTP_400_BAD_REQUEST)
          serializer = TaskSerializer(instance=task, data=request.data, partial=True)
          if serializer.is_valid():
               tsk = serializer.save()
               if tsk.state == 'DE':
                    tsk.update_points()
               return Response(serializer.data, status=status.HTTP_200_OK)
          return Response(serializer.errors, status=status.HTTP_404_BAD_REQUEST)

     
class TaskCollaboratorsView(APIView):
     def put(self, request, pk, format=None):
        try:
            task = Task.objects.get(pk=pk)
            user = CustomUser.objects.get(user=request.user)
            task.collaborators.add(user)
            task.save()
            serializer = TaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
     


#User auth
class RegisterView(APIView):
     def post(self, request, format=None):
          serializer = UserSerializer(data=request.data)
          if serializer.is_valid():
               user = serializer.save()
               user.set_password(request.data['password'])
               user.save()
               prof = request.data['is_professor']
               info = CustomUser(user=user, is_professor=prof)
               info.save()
               return Response(status=status.HTTP_201_CREATED)
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     

class LogoutView(APIView):
     permission_classes = (IsAuthenticated,)

     def post(self, request):
          try:
               refresh_token = request.data["refresh_token"]
               token = RefreshToken(refresh_token)
               token.blacklist()
               return Response(status=status.HTTP_205_RESET_CONTENT)
          except Exception as e:
               return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)