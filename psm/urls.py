# importing django routing libraries
from . import views
from django.urls import path, include
from .views import *

urlpatterns = [
	# home page to blog
	#path('', views.IndexView.as_view(), name='project_index'),
	path('project/', views.projectListView.as_view(), name='project_list'),
	path('project/<pk>/', views.projectDetail.as_view(), name='project_detail'),
	path('projectchart/', views.projectChartView.as_view(), name='project_chart_plan'),
	# path('projectchartactual/', views.projectChartActualView.as_view(), name='project_chart_actual'),
]
