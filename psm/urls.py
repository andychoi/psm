# importing django routing libraries
from . import views
from django.urls import path,  re_path,  include
from .views import *

# app_name="psm"

urlpatterns = [
	# home page to blog
	#path('', views.IndexView.as_view(), name='project_index'),
	path('project-list1/', views.projectList1View.as_view(), name='project_list1'),
	path('project-list2/', views.projectList2View.as_view(), name='project_list2'),
	# path('project-list2/', views.project_list2, name='project_list2'),
	
	re_path(r'^project/(?P<pk>\d+)/$', views.projectDetail.as_view(), name='project_detail'),

	# TODO for customer to submit project request
	# path('project/<int:id>/update', views.project_update, name='project-update'),
	# path('project/<int:id>/delete', views.projectDeleteView.as_view(), name='project-delete'),

	path('projectchart/', views.projectChartView.as_view(), name='project_chart_plan'),
	# path('projectchartactual/', views.projectChartActualView.as_view(), name='project_chart_actual'),
	path('projectchart2/', views.projectChartView2.as_view(), name='project_chart_plan2'),

	path('project-plan/', views.projectPlanListView.as_view(), name='project_plan'),
	re_path(r'^project-plan/(?P<pk>\d+)/$', views.projectPlanDetailView.as_view(), name='project_plan_detail'),

	path('api/1.0/', include('apis.urls')),
]
