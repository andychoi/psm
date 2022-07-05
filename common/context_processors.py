# common/context_processors.py

from django.conf import settings

def my_context(request):
    context_data = dict()
    context_data['my_sub_project'] = settings.MY_PROJECT.upper()
    return context_data