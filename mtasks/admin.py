from adminfilters.multiselect import UnionFieldListFilter
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _
from .models import Task, Item, TASK_PRIORITY_FIELDS
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

# permission
# https://stackoverflow.com/questions/23410306/add-permission-to-django-admin

class ItemInline(admin.TabularInline):
    model = Item
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'user', 'CBU', 'created_at', 'deadline', 'priority', 'state')
    list_display_links = ('project', 'title')
    search_fields = ('id', 'title', 'project', 'project__title', 'item__item_description',
                     'user__name')
    list_filter = (
        ('user', RelatedDropdownFilter),
        ('CBU', RelatedDropdownFilter),
        ('state', UnionFieldListFilter),
        ('priority', UnionFieldListFilter),
        'deadline'
    )
    ordering = TASK_PRIORITY_FIELDS
    readonly_fields = ('created_at', 'last_modified', 'created_by')
    autocomplete_fields = ['user', 'CBU']

    fieldsets = (               # Edition form
        (None,                   {'fields': (('title','project' ), ('user', 'CBU'), 'deadline',
                                             ('state', 'priority'), ('description', 'resolution'))}),
        (_('More...'), {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
    )
    inlines = [ItemInline]

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 4, 'cols': 32})
        }
    }

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('title', 'project'), ('user', 'CBU'), 'deadline', ('state', 'priority'), 'description')}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
