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
from common.models import Div, Dept, PHASE, PRIORITIES, CBU
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

        context['filterItems'] = []

        context['filterItems'].append( {
            "key": "YEAR", "text": "Year", "qId": "year"
            , "selected": self.request.GET.get('year', '')
            , "items": map( lambda x: {"id": x['year'], "name": x['year']}, Project.objects.values('year').distinct() )
        } )

        context['filterItems'].append( {
            "key": "DIV", "text": "Div", "qId": "div"
            , "selected": self.request.GET.get('div', '')
            , "items": Div.objects.all()
        } )

        context['filterItems'].append( {
            "key": "DEP", "text": "Dept.", "qId": "dep"
            , "selected": self.request.GET.get('dep', '')
            , "items": Dept.objects.all()
        } )
    
        context['filterItems'].append( {
            "key": "PHASE", "text": "Phase", "qId": "phase"
            , "selected": self.request.GET.get('phase', '')
            , "items": [{"id": i, "name": x[1]} for i, x in enumerate(PHASE)]
        } )

        context['filterItems'].append( {
            "key": "CBU", "text": "CBU", "qId": "cbu"
            , "selected": self.request.GET.get('cbu', '')
            , "items": CBU.objects.all()
        } )

        context['filterItems'].append( {
            "key": "PRI", "text": "Priority", "qId": "pri"
            , "selected": self.request.GET.get('pri', '')
            , "items": [{"id": i, "name": x[1]} for i, x in enumerate(PRIORITIES)]
        } )

        return context

    def get_queryset(self):
        # # self.year = get_object_or_404(self.year, name=self.kwargs['year'])
        # # return Project.objects.filter(year=self.year).order_by('dept')
        # queryset = Project.objects.filter(year=self.kwargs['year'])

        queryset = Project.objects.all()
        ltmp = self.request.GET.get('year', '')
        if ltmp:
            queryset = queryset.filter(year=ltmp)

        ltmp = self.request.GET.get('div', '')
        if ltmp:
            queryset = queryset.filter(div__id=ltmp)

        ltmp = self.request.GET.get('dep', '')
        if ltmp:
            queryset = queryset.filter(dept__id=ltmp)

        ltmp = self.request.GET.get('phase', '')
        if ltmp:
            queryset = queryset.filter(phase=common.PHASE[int(ltmp)][0])

        ltmp = self.request.GET.get('cbu', '')
        if ltmp:
            queryset = queryset.filter(CBU__id=ltmp)

        ltmp = self.request.GET.get('pri', '')
        if ltmp:
            queryset = queryset.filter(priority=common.PRIORITIES[int(ltmp)][0])

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
