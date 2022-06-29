from django.shortcuts import reverse
from admin_auto_filters.filters import AutocompleteFilter


class StaffFilter(AutocompleteFilter):
    title = 'Staff'
    field_name = 'staff'

    def get_autocomplete_url(self, request, model_admin):
        return reverse('admin:custom_search')