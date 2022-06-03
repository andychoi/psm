# importing django routing libraries
from . import views
from django.urls import path, include
from .views import *

# app_name="psm"

urlpatterns = [
	# home page to blog
	#path('', views.IndexView.as_view(), name='project_index'),
	path('projectlist/', views.projectList1View.as_view(), name='project_list1'),
	path('projectlist2/', views.projectList2View.as_view(), name='project_list2'),
	path('project/<pk>/', views.projectDetail.as_view(), name='project_detail'),
	path('projectchart/', views.projectChartView.as_view(), name='project_chart_plan'),
	# path('projectchartactual/', views.projectChartActualView.as_view(), name='project_chart_actual'),
]
