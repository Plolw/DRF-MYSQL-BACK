from django.urls import path
from . import views
urlpatterns = [
     path('logout/', views.LogoutView.as_view(), name='logout'),
     path('register/', views.RegisterView.as_view(), name='register'),
     path('projects/', views.ProjectsView.as_view(), name='projects'),
     path('projects/<int:pk>/collaborators/', views.ProjectCollaboratorsView.as_view(), name='collaborators'),
     path('projects/<int:pk>/teachers/', views.ProjectTeachersView.as_view(), name='teachers'),
     path('projects/<int:pk>/tasks/', views.TasksView.as_view(), name='tasks')
]