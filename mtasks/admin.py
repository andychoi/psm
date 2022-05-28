from adminfilters.multiselect import UnionFieldListFilter
from django.contrib import admin
from django.contrib import messages
from django.db import models
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _
from .models import Task, TaskItem, TASK_PRIORITY_FIELDS, TaskType
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

# permission
# https://stackoverflow.com/questions/23410306/add-permission-to-django-admin

@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description','is_active')
    list_display_links = ('name',)
    ordering = ('name',)

    class Meta:
        model = TaskType
        import_id_fields = ('id',)

class TaskItemInline(admin.TabularInline):
    model = TaskItem
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('project', 'ttype', 'title', 'user', 'CBU', 'created_at', 'deadline', 'priority', 'state')
    list_display_links = ('project', 'title')
    search_fields = ('id', 'title', 'project', 'project__title', 'taskitem__item_description',
                     'user__name')
    list_filter = (
        ('ttype', RelatedDropdownFilter),
        ('user', RelatedDropdownFilter),
        ('CBU', RelatedDropdownFilter),
        ('state', UnionFieldListFilter),
        ('priority', UnionFieldListFilter),
        'deadline'
    )
    ordering = TASK_PRIORITY_FIELDS
    readonly_fields = ('created_at', 'last_modified', 'created_by')
    autocomplete_fields = ['user', 'CBU']

    # fieldsets = (               # Edition form
    #     (None,                   {'fields': (('title','project' ), ('user', 'CBU'), 'deadline',
    #                                          ('state', 'priority'), ('description', 'resolution'))}),
    #     (_('More...'), {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
    # )
    inlines = [TaskItemInline]

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 4, 'cols': 50})
        }
    }

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (       # Creation form
                (None, {'fields': (('title', 'ttype', 'project'), ('user', 'CBU'), 'deadline', ('state', 'priority'), 'description')}),
            )
        else:
            fieldsets = (       # Edition form
                (None,                   {'fields': (('title', 'ttype', 'project' ), ('user', 'CBU'), 'deadline',
                                                    ('state', 'priority'), ('description', 'resolution'))}),
                (_('More...'), {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
            )            
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        else:
            # check if field_1 is being updated
            #breakpoint()
            if obj._loaded_values['state'] != obj.state and not request.user.has_perm('mtasks.change_status', obj):
                messages.set_level(request, messages.ERROR)
                messages.error(request, "You don't have permission to change state")
                return
            
        super().save_model(request, obj, form, change)

            # ('assign_task', 'Assign task'),
            # ('change_status', 'Change status'),
            # ('close_task', 'Close task'),
# https://stackoverflow.com/questions/23361057/django-comparing-old-and-new-field-value-before-saving            
# https://django-guardian.readthedocs.io/en/stable/userguide/check.html#standard-way
# >>> joe.has_perm('sites.change_site')     #Site objects
# False
# >>> site = Site.objects.get_current()     #Site instance
# >>> joe.has_perm('sites.change_site', site)
# False