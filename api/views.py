from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Project, Task, PointsProject, Invitation
from .serializers import UserSerializer, ProjectSerializer, TaskSerializer, PointsProjectSerializer, InvitationSerializer, CustomUserSerializer
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import date


class ProjectsView(APIView):
     permission_classes = (IsAuthenticated, )

     def get(self, request): #Devuelve todos los proyectos en los que está el usuario que hace la petición 
          user = CustomUser.objects.get(user=request.user)
          projects = Project.objects.filter(Q(creator=user) | Q(collaborators__in=[user])).all()
          serializer = ProjectSerializer(projects, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)

     def post(self, request): #Crea un proyecto y asigna como creador y colaborador al usuario que hace la petición
          serializer = ProjectSerializer(data=request.data)
          user = CustomUser.objects.get(user=request.user)
          if serializer.is_valid():
               proj = Project(creator=user, name=serializer.validated_data.get('name'), description=serializer.validated_data.get('description'))
               proj.save()
               proj.collaborators.add(user)
               proj.save()
               return Response(serializer.data, status=status.HTTP_201_CREATED)
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
     def delete(self, request, pk): #Elimina el proyecto específicado en la url (por la id) siempre que el usuario que hace la peitición sea un colaborador
          project = get_object_or_404(Project, pk=pk)
          user = CustomUser.objects.get(user=request.user)
          if user not in project.collaborators.all():
               return Response({"message": "Can't delete a project if you are not a collaborator!"})
          project.delete()
          return Response({"message": "Project deleted."}, status=status.HTTP_204_NO_CONTENT)

class ProjectTeachersView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk): #Añade al usuario que hace la petición a la lista de profesores que supervisan el proyecto especificado en la url (solo si es un profesor)
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
     permission_classes = (IsAuthenticated,)

     def get(self, request, pk): #Devuelve todas las tareas del proyecto específicado en la url si el usuario que hace la petición es un colaborador o un profesor
          proj = get_object_or_404(Project, pk=pk)
          user = CustomUser.objects.get(user=request.user)
          if user not in proj.collaborators.all() and user not in proj.teachers.all():
               return Response({"message": "Can't see tasks if you are not a collaborator or a teacher!"}, status=status.HTTP_400_BAD_REQUEST)
          tasks = Task.objects.filter(project=proj).all()
          serializer = TaskSerializer(tasks, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)

     def post(self, request, pk): #Crea una tarea en el proyecto específicado en la url
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
     
     def put(self, request, pk): #Modifica los datos de una tarea especificada (los datos se mandan en el request.data) si el usuario que hace la petición es un colaborador
          task = get_object_or_404(Task, pk=pk)
          user = CustomUser.objects.get(user=request.user)
          if user not in task.project.collaborators.all():
               return Response({"message": "Can't change a task if you are not a collaborator!"}, status=status.HTTP_400_BAD_REQUEST)
          serializer = TaskSerializer(instance=task, data=request.data, partial=True)
          if serializer.is_valid():
               tsk = serializer.save()
               if tsk.state == 'DE' and tsk.finish_date == date(2000, 1, 1): #Si la modificación establece el estado de la tarea como "Deployed" suma los story points de dicha tarea a los colaboradores
                    tsk.update_points()
                    tsk.finish_date = date.today() #Además establece la fehca de finalización de la tarea en el dia que se haga la petición
                    tsk.save()
               return Response(serializer.data, status=status.HTTP_200_OK)
          return Response(serializer.errors, status=status.HTTP_404_BAD_REQUEST)
     
     def delete(self, request, pk): #Elimina la tarea especificada si el usuario que hace la petición es un colaborador del proyecto en el que está contenida
          task = get_object_or_404(Task, pk=pk)
          user = CustomUser.objects.get(user=request.user)
          if user not in task.project.collaborators.all():
               return Response({"message": "You are not a collaborator so you can't delete this project's tasks."}, status=status.HTTP_400_BAD_REQUEST)
          task.delete()
          return Response({"message": "Task deleted."}, status=status.HTTP_204_NO_CONTENT)
     
class TaskCollaboratorsView(APIView):
     permission_classes = (IsAuthenticated,)

     def put(self, request, pk): #Añade al usuario que hace la petición a los colaboradores de la tarea especificada
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
        
#Points management
class ProjectUsersPoints(APIView):
     permission_classes = (IsAuthenticated,)

     def get(self, request, pk): #Devuelve los puntos de todos los usuarios del proyecto especificado (solo si el usuario que hace la petición es un colaborador o un profesor)
          pj = get_object_or_404(Project, pk=pk)
          user = CustomUser.objects.get(user=request.user)
          if (user not in pj.collaborators.all()) and (user not in pj.teachers.all()):
               return Response({"message": "Can't access if you are not a collaborator or a teacher!"}, status=status.HTTP_400_BAD_REQUEST)
          points = PointsProject.objects.filter(project_id=pk).all()
          serializer = PointsProjectSerializer(points, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)
     
#Invites
class InvitesView(APIView):
     permission_classes = (IsAuthenticated,)

     def get(self, request): #Devuelve las invitaciones recividas por el usuario que hace la petición
          user = CustomUser.objects.get(user=request.user)
          invites = Invitation.objects.filter(receiver=user).all()
          serializer = InvitationSerializer(invites, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)
     
     def post(self, request, pk=None): #Crea una invitación del usuario que hace la petición a otro usuario (especificado por su nombre de usuario en request.data) a un proyecto especificado en la url
          if pk == None:
               return Response({"message": "No project id, url format '.../invitations/<id>'"}, status=status.HTTP_400_BAD_REQUEST)
          user = CustomUser.objects.get(user=request.user)
          project = get_object_or_404(Project, pk=pk)
          if user not in project.collaborators.all():
               return Response({"message": "Can't invite if you are not a collaborator!"}, status=status.HTTP_400_BAD_REQUEST)
          receiverUser =  get_object_or_404(User, username=request.data['username'])
          receiver = CustomUser.objects.get(user=receiverUser)
          invitation = Invitation(sender=user, receiver=receiver, project=project)
          invitation.save()
          serializer = InvitationSerializer(invitation)
          return Response(serializer.data, status=status.HTTP_201_CREATED)
     
     def put(self, request, pk=None): #Cambia el estado de la invitación especificada por el usuario que hace la petición
          if pk == None:
               return Response({"message": "No invitation id, url format '.../invitations/<id>'"}, status=status.HTTP_400_BAD_REQUEST)
          invitation = get_object_or_404(Invitation, pk=pk)
          
          serializer = InvitationSerializer(instance=invitation, data=request.data, partial=True)
          user = CustomUser.objects.get(user=request.user)
          if user != invitation.receiver:
               return Response({"message": "Can't modify a invitation that's not for you!"}, status=status.HTTP_400_BAD_REQUEST)
          if serializer.is_valid():
               if request.data['state'] == 'AC':
                    try:
                         project = invitation.project
                         if user.is_professor:
                              project.teachers.add(user)
                         else:
                              project.collaborators.add(user)
                         project.save()
                         serializer = ProjectSerializer(project)
                         return Response({"message": "Invitation accepted succesfully!"}, status=status.HTTP_200_OK)
                    except Project.DoesNotExist:
                         return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
                    except Exception as e:
                         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
               elif request.data['state'] == 'DE':
                    invitation.delete()
                    return Response({"message": "Invitation denied and deleted."}, status=status.HTTP_204_NO_CONTENT)
               serializer.save()
               return Response(serializer.data, status=status.HTTP_200_OK)
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#User auth
class RegisterView(APIView):
     def post(self, request): #Registra un usuario con los datos especificados en request.data
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

     def post(self, request): #Cierra la sesión del usuario que hace la petición poniendo su access token en una blacklist (si el token está ahi no permite el acceso)
          try:
               refresh_token = request.data["refresh_token"]
               token = RefreshToken(refresh_token)
               token.blacklist()
               return Response(status=status.HTTP_205_RESET_CONTENT)
          except Exception as e:
               return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
          
class UserView(APIView):
     permission_classes = (IsAuthenticated,)

     def get(self, request, format=None): #Devuelve la información del usuario que hace la petición
          user = CustomUser.objects.get(user=request.user)
          serializer = CustomUserSerializer(user)
          return Response(serializer.data, status=status.HTTP_200_OK)