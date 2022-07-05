# common/adminfilters.py
# https://django-autocomplete-light.readthedocs.io/en/master/tutorial.html#overview

from django.db.models import Q
from users.models import Profile

from dal import autocomplete
class ProfileAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Profile.objects.none()

        qs = Profile.objects.filter(proxy_name='Profile')

        if self.q:
            qs = qs.filter(Q(name__contains=self.q) | Q(email__contains=self.q) | Q(user__username__contains=self.q) )

        return qs