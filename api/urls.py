from django.urls import path
from . import views
urlpatterns = [
     path('logout/', views.LogoutView.as_view(), name='logout'),
     path('register/', views.RegisterView.as_view(), name='register'),
     path('projects/', views.ProjectsView.as_view(), name='projects'),
     path('projects/<int:pk>/collaborators/', views.ProjectCollaboratorsView.as_view(), name='collaborators'),
     path('projects/<int:pk>/teachers/', views.ProjectTeachersView.as_view(), name='teachers'),
     path('projects/<int:pk>/tasks/', views.TasksView.as_view(), name='tasks'),
     path('projects/tasks/<int:pk>/collaborators/', views.TaskCollaboratorsView.as_view(), name='task_collaborators'),
     path('projects/<int:pk>/points/', views.ProjectUsersPoints.as_view(), name='points'),
     path('invitations/<int:pk>/', views.InvitesView.as_view(), name='invitations_put'),
     path('invitations/', views.InvitesView.as_view(), name='invitations')
]