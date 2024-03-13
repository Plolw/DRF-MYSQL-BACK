from django.contrib import admin
from .models import CustomUser, Project, Task, PointsProject, Invitation

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(PointsProject)
admin.site.register(Invitation)