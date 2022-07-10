from django.shortcuts import render
from django.views import generic, View
from django.views.generic.edit import FormView
from django import forms
# from .models import SAP
from datetime import date
from common.models import Div, Dept, CBU
import pandas as pd

# Create your views here.
from .sap import get_opex_summary, get_opex_items

class opex_summary(generic.ListView):
    template_name = 'sap/opex_summary.html'
    context_object_name = 'items'    

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs) #dict
        # q =  {k:v for k, v in self.request.GET.items() if v and hasattr(Project, k.split('__')[0] ) }

        # year = self.request.GET.get('year', date.today().year)
        items = get_opex_summary()
        context['items'] = items 
        context['months'] = [1,2,3,4,5,6,7,8,9,10,11,12]

        return context

    def get_queryset(self):
        # q =  {k:v for k, v in self.request.GET.items() if v and hasattr(Project, k.split('__')[0] ) }
        return None


# class OpexForm(forms.ModelForm):
#     year = forms.IntegerField()
#     cc = forms.CharField(max_length=10)
#     # employee = forms.ModelChoiceField(queryset=Employee.objects.all(), to_field_name="id")

#     class Meta:
#         model = SAP
#         fields = ('year', 'cc')

def opex_items(request):
    # template_name = 'sap/opex_items.html'

    context = {}
    # context['form'] = OpexForm()    #tip django ListView with a form
    # year = self.request.GET.get('year', date.today().year)
    items = get_opex_items()

    df = pd.DataFrame(items)
    cclist1 = df['KOSTV'].unique().tolist()  #unique distinct from df column
    cclist2 = df.drop_duplicates(['KOSTV','CCTEXT'])[['KOSTV','CCTEXT']].values.tolist()     # df to list array
    # cclist2 = df.drop_duplicates(['KOSTV','CCTEXT'])[['KOSTV','CCTEXT']].to_dict('records')     # df to dict array
    context['cclist'] = cclist2 
    context['months'] = [1,2,3,4,5,6,7,8,9,10,11,12]

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        # form = OpexForm(request.POST)
        # if form.is_valid():
        
        # select items based on form filters 
        context['items'] = items 

    else:
        pass
        # context['items'] = items 

    get_filter_options(request, context)

    return render(request, 'sap/opex_items.html', context)


def get_filter_options(request, context, def_year=True, plan=False):
    # For side filter
    context['filterItems'] = []
    
    get_def_year = '' if not def_year else date.today().year if not request.GET.get('year', '') else request.GET.get('year', '') 

    context['filterItems'].append( { "key": "YEAR", "text": "Year", "qId": "year", "selected": get_def_year
        , "items": [{"id": x, "name": x} for x in { '2021', '2022', '2023' } ]
        } )

    #TODO based on actual or master based??
    context['filterItems'].append( {
    "key": "DIV", "text": "Div", "qId": "div", "selected": request.GET.get('div', ''), "items": Div.objects.all()
    } )

    context['filterItems'].append( {
        "key": "DEP", "text": "Dept.", "qId": "dept", "selected": request.GET.get('dept', ''), "items": Dept.objects.all()
        # "key": "DEP", "text": "Dept.", "qId": "dept__name", "selected": self.request.GET.get('dept__name', ''), "items": [{ "id": x[0], "name":x[0]} for i, x in Dept.objects.all().values_list('name') ]
    } )
    
    # context['filterItems'].append( {
    #     "key": "CBU", "text": "CBU", "qId": "cbu", "selected": request.GET.get('cbu', '')
    #     , "items": CBU.objects.filter(is_active=True)
    # } )
