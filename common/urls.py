from django.urls import path, re_path

from .adminfilters import *

urlpatterns = [

    re_path('admin-filter/profile-staff-autocomplete/', ProfileAutocomplete.as_view(), name='profile-staff-autocomplete',    ),
    
]
