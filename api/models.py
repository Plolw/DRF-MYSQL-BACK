from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Project(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects', null=True)
    collaborators = models.ManyToManyField(User, related_name='collaborating_projects', blank=True)
    name = models.CharField(max_length=30)

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', null=True)
    name = models.CharField(max_length=30)
    start_date = models.DateField()
    finish_date = models.DateField()

    
