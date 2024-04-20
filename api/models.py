from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Create your models here.

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_user', null=True)
    is_professor = models.BooleanField(default=False)
    
    def get_project_SP(self, p_id):
        return self.points.filter(project_id=p_id)

    def save_points(self, p_id, pnts): #Guardar puntos de un usuario en un proyecto
        points = PointsProject(user=self, project_id=p_id, points=pnts, date=timezone.now().date())
        points.save()
    
class Project(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_projects', null=True)
    collaborators = models.ManyToManyField(CustomUser, related_name='collaborating_projects', blank=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    teachers = models.ManyToManyField(CustomUser, related_name='observed_projects', blank=True)

class Task(models.Model):
    CHOICES = [ #Opciones de estado de la tarea
        ('AN', 'Analizando'),
        ('CU', 'En curso'),
        ('RE', 'En review'),
        ('DE', 'Deployed')
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_tasks', null=True)
    collaborators = models.ManyToManyField(CustomUser, related_name='collaborating_tasks', blank=True)
    previous_task = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='next_tasks', null=True, blank=True)
    next_task = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='previous_tasks', null=True, blank=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    start_date = models.DateField()
    finish_date = models.DateField(default=("2000-01-01"))
    story_points = models.IntegerField()
    state = models.CharField(max_length=20, choices=CHOICES, default='AN')#C
    estimated_hours = models.FloatField()
    total_hours = models.FloatField(default=0)

    def update_points(self): #Actualizar puntos de un proyecto repartiendo los de la tarea utilizada entre sus colaboradores
        if self.collaborators.count() < 2:
            points_per_usr = self.story_points
        else:
            points_per_usr = self.story_points / self.collaborators.count()
        for collaborator in self.collaborators.all():
            collaborator.save_points(self.project.id, points_per_usr)

class PointsProject(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='story_points', null=True)
    project_id = models.IntegerField()
    points = models.FloatField()
    date = models.DateField(default=("2000-01-01"))

class Invitation(models.Model):
    CHOICES = [ #Opciones de estado de la invitación (se guardan abreviados en la base de datos)
        ('AC', 'Accepted'),
        ('WA', 'Waiting'),
        ('DE', 'Denied')
    ]

    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='s_invitations')  #CAMBIOS!!!
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='r_invitations') #CAMBIOS!!!
    state = models.CharField(max_length=20, choices=CHOICES, default='WA')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='p_invitations', null=True) #CAMBIOS!!!