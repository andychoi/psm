# importing models and libraries
from django.shortcuts import render
from .models import Report, Milestone
from django.views import generic

# https://medium.com/@ksarthak4ever/django-class-based-views-vs-function-based-view-e74b47b2e41b
# class based vs. function based views

# class IndexView(generic.ListView):
#     template_name = 'reports/index.html'
#     context_object_name = 'latest_report_list'
	
# 	def get_queryset(self):
# 		return Report.objects.order_by('-updated_on')[:25]
		
# class based views for reports -> for selected project
class reportList(generic.ListView):
	queryset = Report.objects.filter(status=1).order_by('-updated_on')
	template_name = 'reports/report_list.html'
	paginate_by = 100
	context_object_name = 'report_list'


# class based view for each report
class reportDetail(generic.DetailView):
	model = Report
	template_name = "reports/report_detail.html"
	context_object_name = 'report_detail'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)    
		context['milestone'] = Milestone.objects.filter(report=self.object).order_by('no')
		return context

# how to pass multiple object
# -> https://stackoverflow.com/questions/42250375/django-passing-multiple-objects-to-templates-but-nothing-in-there

