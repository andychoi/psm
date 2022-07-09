from django.shortcuts import render
from django.views import generic, View

# Create your views here.
from .sap import get_opex_summary

# - how to provide my project for PM, HOD
class opex_summary(generic.ListView):
    template_name = 'sap/opex_summary.html'
    context_object_name = 'items'    

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs) #dict
        # q =  {k:v for k, v in self.request.GET.items() if v and hasattr(Project, k.split('__')[0] ) }

        # year = self.request.GET.get('year', date.today().year)
        items = get_opex_summary()

        return context

    def get_queryset(self):
        # q =  {k:v for k, v in self.request.GET.items() if v and hasattr(Project, k.split('__')[0] ) }
        return None