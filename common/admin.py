from collections import defaultdict
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from django.contrib import messages
from import_export import resources, fields
from django.core.exceptions import ValidationError
from django.conf import settings
from django_object_actions import DjangoObjectActions

from .models import CompanyHoliday, CBU, Div, Dept, Team, GMDM

from django.contrib.auth.models import User, Group

from django.db.models import Count, F, Q, Sum, Avg, Subquery, OuterRef, When, Case, IntegerField

from django.contrib.auth.models import Permission
from django.contrib import admin
from django.shortcuts import redirect
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from adminfilters.multiselect import UnionFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter, ChoiceDropdownFilter

from pyrfc import Connection
from django.conf import settings
from django.utils import timezone
from users.models import User
import pytz
from django.http import HttpResponseRedirect
from django.urls import reverse


import logging
logger = logging.getLogger(__name__)



@admin.register(CompanyHoliday) 
class CompanyHolidayAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('year','subdiv', 'holiday')    
    list_filter = ('year', 'subdiv', )

    actions = ['copy_to_next_year']
    @admin.action(description="Copy to next year", permissions=['change'])
    def copy_to_next_year(self, request, queryset):
        for obj in queryset:
            obj.id = None
            obj.year = obj.year + 1
            obj.holiday += relativedelta(years=1)
            obj.save()
            messages.add_message(request, messages.INFO, ' is copied/saved')


@admin.register(Permission) 
class PermissionAdmin(admin.ModelAdmin):
    model = Permission
    fields = ['name', 'codename']
    search_fields = ('name','codename')    
    list_display = ('name','codename')    

# Register your models here.
@admin.register(Div)
class DivAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'head', 'is_active', 'cc', 'em_count', 'pm_count')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'cc', 'head__name', 'head__auto_id')    
    autocomplete_fields = ('head',)
    ordering = ('cc', )
    class Meta:
        model = Div
        import_id_fields = ('id',)

# Register your models here.
@admin.register(Dept)
class DeptAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'head', 'div', 'is_active', 'is_virtual', 'cc', 'em_count', 'pm_count', 'notes')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'cc', 'head__name', 'head__auto_id')    
    autocomplete_fields = ('head',)
    ordering = ('cc', )
    class Meta:
        model = Dept
        import_id_fields = ('id',)
        
@admin.register(Team)
class TeamAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'head', 'dept', 'is_active', 'cc', 'em_count', 'pm_count')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'cc', 'head__name', 'head__auto_id')
    autocomplete_fields = ('head',)
    ordering = ('cc', )
    class Meta:
        model = Team
        import_id_fields = ('id',)


@admin.register(CBU)
class CBUAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'fullname', 'group', 'is_tier1', 'cbu_type')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'full_name')

    ordering = ('id', 'name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_on', )
    fieldsets = (  # Edition form
#        (None, {'fields': (('name', 'is_company'), ('email', 'website'), ('phone', 'mobile'), ('address',), ('comment',))}),
         (None, {'fields': (('name', 'cbu_type', 'is_tier1', 'is_active'), ('fullname', 'group') , ('comment',))}),
        (_('More...'), {'fields': (('created_at', 'updated_on') ), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('name', 'cbu_type', 'is_tier1', 'is_active'), ('fullname', 'group'), ('comment',))}),
#                (None, {'fields': (('name', 'is_company'), ('email', 'website'), ('phone', 'mobile'), ('address',), ('comment',))}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    class Meta:
        model = CBU
        import_id_fields = ('id',)


""" system inventory
"""
class GMDMResource(resources.ModelResource):
    from users.models import Profile
    dept_name  = fields.Field(attribute='dept',widget=ForeignKeyWidget(model=Dept, field='name'), )
    team_name  = fields.Field(attribute='team',widget=ForeignKeyWidget(model=Team, field='name'), )
    CBU_name   = fields.Field(attribute='CBU',widget=ForeignKeyWidget(model=CBU, field='name'), )
    # owner1_name   = fields.Field(attribute='owner1',widget=ForeignKeyWidget(model=Profile, field='name'), )
    class Meta:
        model = GMDM
        fields = ( 'id', 'code', 'CBU', 'CBU_name', 'CBUteam', 'name', 'severity', 'outline', 
            'platform', 'os', 'db', 'lang', 'ui', 'apptype', 'no_screen', 'no_if', 'no_table', 'usertype', 'no_user',
            'operator', 'sme', 'assignment', 'assignee', 'manager', 'hod', 'is_bot',
            'grouping', 'dept', 'dept_name', 'team', 'team_name', 
            'level1', 'level2', 'status', 'initial', 'latest', 'decommission', 'remark',  
        )
       
@admin.register(GMDM)
class GMDMAdmin(DjangoObjectActions, ImportExportMixin, admin.ModelAdmin):
    resource_class = GMDMResource
    class Meta:
        model = GMDM
        import_id_fields = ('id',)    

    list_display = ('code', 'name', 'CBU','hod', 'manager', 'sme', 'assignee', 'assignment', 'is_bot', 'grouping')
    list_display_links = ('code', 'name')
    # list_editable = ('sme', 'assignee',  )
    readonly_fields = ('created_at', 'updated_on', 'created_by', 'updated_by', )
    search_fields = ('id', 'code', 'name')
    # autocomplete_fields = ('dept',)
    ordering = ('dept', 'team', 'code', )
    search_fields = ('id', 'code', 'name', 'outline', 'sme', 'assignee', 'manager', 'assignment', 'grouping', 'ui')
    list_filter = (
        ('CBU',           RelatedDropdownFilter),
        ('is_bot',            DropdownFilter),
        ('operator',            DropdownFilter),
        ('hod',            DropdownFilter),
        ('manager',            DropdownFilter),
        ('sme',            DropdownFilter),
        ('assignee',            DropdownFilter),
        ('assignment',            DropdownFilter),
        # ('owner1__name',        DropdownFilter),   
        # ('owner2__name',        DropdownFilter),
        ('dept',          RelatedDropdownFilter),
        ('team',          RelatedDropdownFilter),
        ('severity',            DropdownFilter),
        ('apptype',             DropdownFilter),
        ('grouping',            DropdownFilter),
    )
    autocomplete_fields = ['team',  ]

    gmdm_fields = [ ('code', 'name', 'CBU', 'severity',  ),
                    ('outline','remark' ), 
                    ('platform', 'os', 'db', 'lang', 'ui','apptype'),
                    ('no_screen', 'no_if', 'no_table', 'usertype', 'no_user', ), 
                    ('operator', 'is_bot', 'sme', 'assignment', 'assignee', 'manager', 'hod'),
                    ('dept', 'team', 'CBUteam'),
                    ('grouping', 'level1', 'level2'),
                    ('status', 'initial', 'latest', 'decommission'),
                    ]
    fieldsets = (               # Edition form
        (None,  {'fields': gmdm_fields 
                , "classes": ("stack_labels",)}),
        (_('More...'), {'fields': ( ('created_at', 'updated_on'), 'created_by', ('attachment'),  ), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None): # Creation form
        return ( (None, { 'fields': self.gmdm_fields  }), )

    def is_active(self, obj):
        return "yes" if not obj.decommission else "no"

    # tip initial default version set
    def get_form(self, request, obj=None, **kwargs):
        form = super(GMDMAdmin, self).get_form(request, obj, **kwargs)
        #FIXME if read-only due to permission
        if hasattr(form, 'base_fields'):
            form.base_fields['outline'     ].widget.attrs.update({'rows':5,'cols':160})

        #permission based field read only....
        if not request.user.has_perm('admin_gmdm'):
            form.base_fields['code'].disabled = True 
            form.base_fields['severity'].disabled = True 

        return form

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user            
        
        super().save_model(request, obj, form, change)

    # FIXME TODO next time
    # def changelist_view(self, request, extra_context=None):
    #     if len(request.GET) == 0:
    #         get_param = "is_active=True"
    #         return redirect("{url}?{get_parms}".format(url=request.path, get_parms=get_param))
    #     return super(GMDMAdmin, self).changelist_view(request, extra_context=extra_context)

    # permission... use get_form 
    # def has_change_permission(self, request, obj=None):
    #     if obj :
    #         if not request.user.has_perm('admin_gmdm'):
    #             return False    
    #         return True
    #     else:
    #         return super(GMDMAdmin, self).has_change_permission(request, obj)

    # def get_queryset(self, request):
    #     return GMDM.objects.all()

    # validation logic
    # def clean(self):
    #     validation_errors = {}

    #     # code change is only allowed for admin TODO
    #     # if not self.user.has_perm('admin_gmdm') and change...
    #     #     validation_errors['code'] = _('You are not allowed to change code')

    #     if len(validation_errors):
    #         raise ValidationError(validation_errors)

    # fix conflict issue with two package: import/export, obj-action
    changelist_actions = ['redirect_to_export', 'redirect_to_import', ]
    def redirect_to_export(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_export' % self.get_model_info()))
    redirect_to_export.label = "Export"
    def redirect_to_import(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_import' % self.get_model_info()))
    redirect_to_import.label = "Import"