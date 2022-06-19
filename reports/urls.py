# importing django routing libraries
from . import views
from django.urls import path, include
from .views import *
from psm.views import projectList3View
#from .feeds import blogFeed

from django.contrib.auth.decorators import login_required

urlpatterns = [

	path('report/test/', 		views.test_view),
	path('report/test/dash', 	views.test_dash),
	path('report/test/chart', 	views.test_chart),
	path('report/test/table', 	views.test_table),
	path('report/test/project', projectList3View.as_view()),
	
	# home page

	#path('', views.IndexView.as_view(), name='index'),
	path('report/risks/', login_required(views.reportRisks.as_view()), 		name='report_risks'),
	path('report/email/<pk>/', login_required(views.reportEmail.as_view()), name='report-email'),
	path('report/', login_required(views.reportList.as_view()), 			name='report_list'),
	path('report/<pk>/', login_required(views.reportDetail.as_view()), 		name='report_detail'),
]
