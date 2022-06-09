import django_filters
from django_filters import DateFilter
from .models import Project
from django import forms

import django_filters
class ProjectFilter(django_filters.FilterSet):
    # client__name = django_filters.CharFilter(lookup_expr='icontains')
    # client__surname = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Project
        exclude = ['attachment']
        fields = {
            'title'         : ['icontains'],
            'description'   : ['icontains'],
            # 'CBUs'          : ['in'],
        }

# https://stackoverflow.com/questions/65565093/styling-django-filter-form-in-html


# class TutorialFilter(django_filters.FilterSet):
#     DATE_CHOICES        = (
#                             ('newest', 'Newest'),
#                             ('oldest', 'Oldest')
#     )
#     date_sort           = django_filters.ChoiceFilter(
#                             label     ='Sort by Date ',
#                             choices   =DATE_CHOICES,
#                             method    ='filter_by_date',
#                             # widget  =forms.Select(attrs={'size': 4})
#     )


#     class Meta:
#         model = Tutorial
#         fields = {
#                             'title'     : ['icontains'],
#                             'instructor': ['icontains'],
#                             'language'  : ['exact'],
#                             'difficulty': ['exact'],
#         }


#     def filter_by_date(self, queryset, name, value):
#         expression = 'last_updated' if value == 'oldest' else '-last_updated'
#         return queryset.order_by(expression)