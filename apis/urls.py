from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.project_list),
    path('projects/update/period/', views.projects_update_period),
    path('project/<int:pk>/', views.project_detail),
]
