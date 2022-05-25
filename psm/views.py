from django.shortcuts import render

# Create your views here.


# importing models and libraries
from django.shortcuts import render
from .models import Project
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

#https://stackoverflow.com/questions/24305854/simple-example-of-how-to-use-a-class-based-view-and-django-filter
#https://stackoverflow.com/questions/57085070/using-django-filter-with-class-detailview
# class based views for project -> for selected project
class projectListView(generic.ListView):
    queryset = Project.objects.all()
    template_name = 'project/project_list.html'
    paginate_by = 4
    context_object_name = 'project_list'    

class projectListViewH(generic.ListView):
    queryset = Project.objects.all()
    template_name = 'project/project_list.html'
    paginate_by = 4
    context_object_name = 'project_listh'    

class projectListViewK(generic.ListView):
    queryset = Project.objects.all()
    template_name = 'project/project_list.html'
    paginate_by = 4
    context_object_name = 'project_listk'    

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
