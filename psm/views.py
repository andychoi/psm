from urllib.request import Request
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.db.models import Q

# Create your views here.


# importing models and libraries
from django.shortcuts import render
from pyparsing import common
from .models import Project
from common.models import CBU, Dept, Div
from django.views import generic


# https://medium.com/@ksarthak4ever/django-class-based-views-vs-function-based-view-e74b47b2e41b
# class based vs. function based views

class IndexView(generic.ListView):
    template_name = 'project/index.html'
    context_object_name = 'latest_project_list'

    def get_queryset(self):
        """Return the last five project."""
        return Project.objects.order_by('-last_modified')[:5]

# https://django-filter.readthedocs.io/ -> error, don't use
# https://django-tables2.readthedocs.io/ -> this is better, but...
# https://mattsch.com/2021/05/28/django-django_tables2-and-bootstrap-table/
# https://bootstrap-table.com/
#https://stackoverflow.com/questions/57085070/using-django-filter-with-class-detailview
#https://stackoverflow.com/questions/24305854/simple-example-of-how-to-use-a-class-based-view-and-django-filter
#https://docs.djangoproject.com/en/2.2/topics/class-based-views/generic-display/#dynamic-filtering
#https://stackoverflow.com/questions/51121661/django-filter-multiple-values
# class based views for project -> for selected project
class projectListView(generic.ListView):
    template_name = 'project/project_list.html'
    model = Project
    paginate_by = 1000
    context_object_name = 'project_list'    
    # selectedCBU = self.request.GET.get('cbu', -1)    
    
    # def get(self, request, *args, **kwargs):
    #     form = self.form_class(initial=self.initial)
    #     return render(request, self.template_name, {'form': form})    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['filter_YEAR'] = {}
        context['filter_YEAR']['selected'] = self.request.GET.get('year', '')
        context['filter_YEAR']['items'] = map( lambda x: {"id": x['year'], "name": x['year']}, Project.objects.values('year').distinct() )

        context['filter_DIV'] = {}
        context['filter_DIV']['selected'] = self.request.GET.get('div', '')
        context['filter_DIV']['items'] = Div.objects.all()

        context['filter_CBU'] = {}
        context['filter_CBU']['selected'] = self.request.GET.get('cbu', '')
        context['filter_CBU']['items'] = CBU.objects.all()
        
        return context

    def get_queryset(self):
        # # self.year = get_object_or_404(self.year, name=self.kwargs['year'])
        # # return Project.objects.filter(year=self.year).order_by('dept')
        # queryset = Project.objects.filter(year=self.kwargs['year'])

        queryset = Project.objects.all()
        lYear = self.request.GET.get('year', '')
        if lYear:
            queryset = queryset.filter(year=lYear)

        lDiv = self.request.GET.get('div', '')
        if lDiv:
            queryset = queryset.filter(div=lDiv)

        lCBU = self.request.GET.get('cbu', '')
        if lCBU:
            queryset = queryset.filter(CBU__id=lCBU)
        return queryset


    # def get_queryset(self):
    #     self.CBU = get_object_or_404(CBU, name=self.kwargs['CBU'])
    #     return Project.objects.filter(CBU=self.CBU).order_by('dept')

class projectListYearView(generic.ListView):
    template_name = 'project/project_list.html'
    model = Project
    paginate_by = 1000
    context_object_name = 'project_list'    

    def get_queryset(self):
        # self.year = get_object_or_404(self.year, name=self.kwargs['year'])
        # return Project.objects.filter(year=self.year).order_by('dept')
        queryset = Project.objects.filter(year=self.kwargs['year'])
        return queryset

class projectListCBUView(generic.ListView):
    # queryset = Project.objects.filter(CBU__group='HMNA')
    template_name = 'project/project_list.html'
    paginate_by = 1000
    context_object_name = 'project_list'    
    def get_queryset(self) :
        queryset = Project.objects.filter(CBU__name=self.kwargs['CBU'])
        return queryset

# class based view for each Project
class projectDetail(generic.DetailView):
	model = Project
	template_name = "project/project_detail.html"
	context_object_name = 'project_detail'

	# def get_context_data(self, **kwargs): --> SSG??
	# 	context = super().get_context_data(**kwargs)    
	# 	context['milestone'] = Milestone.objects.filter(Project=self.object).order_by('no')
	# 	return context

# how to pass multiple object
# -> https://stackoverflow.com/questions/42250375/django-passing-multiple-objects-to-templates-but-nothing-in-there
