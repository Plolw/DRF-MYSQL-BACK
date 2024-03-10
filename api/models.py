from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_user', null=True)
    is_professor = models.BooleanField(default=False)
    
    def get_project_SP(self, p_id):
        return self.points.filter(project_id=p_id)

    def save_poinst(self, p_id, pnts):
        p = self.points.filter(project_id=p_id)
        if p:
            p.points += pnts
            p.save()
        else:
            points = PointsProject(user=self, project_id=p_id, points=pnts)
            points.save()
    
    
class Project(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_projects', null=True)
    collaborators = models.ManyToManyField(CustomUser, related_name='collaborating_projects', blank=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    teachers = models.ManyToManyField(CustomUser, related_name='observed_projects', blank=True)

class Task(models.Model):
    CHOICES = [
        ('AN', 'Analizando'),
        ('CU', 'En curso'),
        ('RE', 'En review'),
        ('DE', 'Deployed')
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_tasks', null=True)
    collaborators = models.ManyToManyField(CustomUser, related_name='collaborating_tasks', blank=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    start_date = models.DateField()
    finish_date = models.DateField()
    story_points = models.IntegerField()
    state = models.CharField(max_length=20, choices=CHOICES)#
    estimated_hours = models.FloatField()
    total_hours = models.FloatField(default=0)

    def update_points(self):
        if self.collaborators.count() < 1:
            points_per_usr = self.story_points
        else:
            points_per_usr = self.story_points / self.collaborators.count()
        for collaborator in self.collaborators.all():
            collaborator.save_points(self.project.id, points_per_usr)

class PointsProject(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='points', null=True)
    project_id = models.IntegerField()
    points = models.FloatField()