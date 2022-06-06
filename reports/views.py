# importing models and libraries
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
# from django_filters import FilterSet
from django.views import generic

from common.utils import Status
from .models import Report, Milestone, ReportRisk

# https://medium.com/@ksarthak4ever/django-class-based-views-vs-function-based-view-e74b47b2e41b
# class based vs. function based views

# class IndexView(generic.ListView):
#     template_name = 'reports/index.html'
#     context_object_name = 'latest_report_list'
	
# 	def get_queryset(self):
# 		return Report.objects.order_by('-updated_on')[:25]
		
# class based views for reports -> for selected project

# https://django-filter.readthedocs.io/en/stable/guide/usage.html#overriding-default-filters
# class ReportFilter(FilterSet):
#     class Meta:
#         model = Report
#         fields = {
#             'title': ['icontains', ],
#             'project__title': ['icontains', ],
#         }

# @login_required(login_url='/example url you want redirect/') #redirect when user is not logged in
# for function based view
class reportList(generic.ListView):
	queryset = Report.objects.filter(status=1).order_by('-id')
	template_name = 'reports/report_list.html'
	paginate_by = 200
	context_object_name = 'report_list'
	
	#FIXME
	def get_queryset(self):
		queryset = super().get_queryset()
		query = self.request.GET.get("project__id")
		if query:
			queryset = queryset.filter(project__id__exact=query)
		return queryset

		
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		queryset = self.get_queryset()

		# django-filter
		# filter = ReportFilter(self.request.GET, queryset)
		# context["filter"] = filter

		return context


# class based view for each report
class reportDetail(generic.DetailView):
	model = Report
	template_name = "reports/report_detail.html"
	context_object_name = 'report_detail'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)    
		context['milestone'] = Milestone.objects.filter(report=self.object).order_by('no')
		# breakpoint()
		return context

class reportEmail(reportDetail):
	template_name = "reports/report_email.html"

# how to pass multiple object
# -> https://stackoverflow.com/questions/42250375/django-passing-multiple-objects-to-templates-but-nothing-in-there


class reportRisks(generic.ListView):
	queryset = ReportRisk.objects.filter(~Q(status=Status.COMPLETED.value)).order_by('-id')
	template_name = 'reports/report_risks.html'
	paginate_by = 10
	context_object_name = 'report_risks'
    
