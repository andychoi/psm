# importing models and libraries
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
# from django_filters import FilterSet
from django.views import generic
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404

from common.codes import State2
from .models import Report, Milestone, ReportRisk
from psm.models import Project
from django.core.paginator import Paginator

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
class reportList(PermissionRequiredMixin, generic.ListView):
	permission_required = 'reports.view_report'
	queryset = Report.objects.filter(status=1).order_by('-id')
	template_name = 'reports/report_list.html'
	paginate_by = 250
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
class reportDetail(PermissionRequiredMixin, generic.DetailView):
	permission_required = 'reports.view_report'	
	model = Report
	template_name = "reports/report_detail.html"
	context_object_name = 'report_detail'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs) 
		context['remainder'] = 100 - self.object.progress
		context['milestone'] = Milestone.objects.filter(report=self.object).order_by('no')
		# breakpoint()
		return context

class reportEmail(reportDetail):
	template_name = "reports/report_email.html"


# how to pass multiple object
# -> https://stackoverflow.com/questions/42250375/django-passing-multiple-objects-to-templates-but-nothing-in-there


class reportRisks(generic.ListView):
	# permission_required = 'reports.view_reportrisk'
	template_name = 'reports/report_risks.html'
	paginate_by = 50
	context_object_name = 'report_risks'
	queryset = ReportRisk.objects.filter(state=State2.OPEN.value).order_by('-id')

class reportRisksProject(generic.ListView):
	# permission_required = 'reports.view_reportrisk'
	template_name = 'reports/report_risks.html'
	paginate_by = 50
	context_object_name = 'report_risks'
	
	def get_queryset(self):
		self.project = get_object_or_404(Project, id=self.kwargs['project'])
		return ReportRisk.objects.filter(project=self.project, state=State2.OPEN.value).order_by('-id')

# def reportRisks(request, project=None):
# 	permission_required = 'reports.view_reportrisk'	
# 	if project:
# 		qs = ReportRisk.objects.filter(Q(project__id=project) & Q(state=State2.OPEN.value)).order_by('-id')
# 	else:
# 		qs = ReportRisk.objects.filter(state=State2.OPEN.value).order_by('-id')
# 	paginator = Paginator(qs, 50)
# 	page = request.GET.get('page')
# 	page_obj = paginator.get_page(page)
# 	context = {'qs': qs, 'report_risks': page_obj}

# 	return render(request, 'reports/report_risks.html', context)

# pass id attribute from urls
def test_view(request): #, id):
    context ={}
 
    # add the dictionary during initialization
    # context["data"] = GeeksModel.objects.get(id = id)
         
    return render(request, "theme/index.html", context)
def test_dash(request):
    return render(request, "theme/dashboard.html")

def test_chart(request):
    return render(request, "theme/charts.html")
def test_table(request):
    return render(request, "theme/tables.html")
def test_pages(request):
    return render(request, "theme/blank.html")
	