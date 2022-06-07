# importing django routing libraries
from . import views
from django.urls import path, include
from .views import *

# app_name="psm"

urlpatterns = [
	# home page to blog
	#path('', views.IndexView.as_view(), name='project_index'),
	path('project-list1/', views.projectList1View.as_view(), name='project_list1'),
	path('project-list2/', views.projectList2View.as_view(), name='project_list2'),
	# path('project-list2/', views.project_list2, name='project_list2'),
	path('project/<pk>/', views.projectDetail.as_view(), name='project_detail'),
	path('projectchart/', views.projectChartView.as_view(), name='project_chart_plan'),
	# path('projectchartactual/', views.projectChartActualView.as_view(), name='project_chart_actual'),

	path('projectchart2/', views.projectChartView2.as_view(), name='project_chart_plan2'),
]
