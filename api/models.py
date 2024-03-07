from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    is_professor = models.BooleanField(default=False)

class Project(models.Model):
    creator = models.ForeignKey(AbstractUser, on_delete=models.CASCADE, related_name='created_projects', null=True)
    collaborators = models.ManyToManyField(AbstractUser, related_name='collaborating_projects', blank=True)
    name = models.CharField(max_length=30)
    teachers = models.ManyToManyField(AbstractUser, on_delete=models.CASCADE, related_name='observed_projects', null=True)

class Task(models.Model):
    CHOICES = [
        ('AN', 'Analizando'),
        ('CU', 'En curso'),
        ('RE', 'En review'),
        ('DE', 'Deployed')
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True)
    creator = models.ForeignKey(AbstractUser, on_delete=models.CASCADE, related_name='created_tasks', null=True)
    collaborators = models.ManyToManyField(AbstractUser, related_name='collaborating_tasks', blank=True)
    name = models.CharField(max_length=30)
    start_date = models.DateField()
    finish_date = models.DateField()
    story_points = models.IntegerField()
    state = models.CharField(max_length=20, choices=CHOICES)#
    estimated_hours = models.FloatField()
    total_hours = models.FloatField()