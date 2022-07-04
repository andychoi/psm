from collections import defaultdict
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from django.contrib import messages
from import_export import resources, fields
from django.core.exceptions import ValidationError
from django.conf import settings

from .models import CompanyHoliday, CBU, Div, Dept, Team, WBS, GMDM, Employee

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


from django_object_actions import DjangoObjectActions


@admin.register(WBS)
class WBSAdmin(DjangoObjectActions, ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'wbs', 'name', 'is_sub', 'cbu', 'status', 'formatted_budget')
    list_display_links = ('wbs', 'name')
    search_fields = ('id', 'wbs', 'name')

    ordering = ('-wbs',)

    readonly_fields = ('created_at', 'updated_on', )
    fieldsets = (  # Edition form
         (None, {'fields': (('wbs', 'name', 'cbu') , ('status', 'budget'))}),
        (_('More...'), {'fields': (('created_at', 'updated_on'), ), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('wbs', 'name', 'cbu') , ('status', 'budget'))}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def formatted_budget(self, obj):
        # obj is the Model instance

        # If your locale is properly set, try also:
        # locale.currency(obj.amount, grouping=True)
        if obj.budget is not None:
            return "$ {:,}".format(obj.budget)        
        #return format_currency(obj.budget , 'USD', locale='en_US', format="#,##0;-#")
    formatted_budget.short_description = 'Budget'    

    # https://github.com/crccheck/django-object-actions -> this is good
    # https://stackoverflow.com/questions/19542295/overridding-django-admins-object-tools-bar-for-one-model
    # change_list_template = 'admin/common/wbs/change_list.html'
    # object function

    def object_func(self, request, obj):
        pass
    # object_func.label = "Obj Func"  
    change_actions = ('object_func', )

    # list function
    # https://stackoverflow.com/questions/24172130/open-sql-condition-in-rfc-read-table-call-via-pyrfc
    # from pyrfc import Connection
    # from pyrfc import Connection, ABAPApplicationError, ABAPRuntimeError, LogonError, CommunicationError
    # from ConfigParser import ConfigParser

    # Table: ZSUSPSV0020
    # FIELDS: PSPID, POST1, STSPD, ...

    def import_func(modeladmin, request, queryset):    
        print(_update_wbs())


    import_func.label = "Import from SAP"  
    import_func.short_description = "This will import WBS data from SAP system" 
    changelist_actions = ('import_func', )

from django.contrib.auth.decorators import user_passes_test
from common.functions import _update_wbs, _update_emp, _update_org, _update_profile, _update_emp_org_profile

@user_passes_test(lambda u: u.is_superuser)
@admin.register(Employee)
class EmployeeAdmin(DjangoObjectActions, ImportExportMixin, admin.ModelAdmin):
    list_display = ('emp_id', 'emp_name', 'email', 'job', 'cc', 'l', 'dept_code', 'dept_name', 'manager_id', 'create_date', 'terminated')
    list_display_links = ('emp_id', )
    search_fields = ('emp_id', 'manager_id', 'emp_name', 'email', 'dept_name', 'cc', 'dept_name')
    ordering = ('emp_id',)

    list_filter = (
        ('terminated',  DropdownFilter),
        ('cc',          DropdownFilter),
        ('dept_name',   DropdownFilter),
        ('manager_id',  DropdownFilter),
    )


    def update_emp_org_profile(modeladmin, request, queryset):    
        print(_update_emp_org_profile())    # in psmprj/cron.py too
    update_emp_org_profile.label = "Refresh from SAP"  

    def update_emp(modeladmin, request, queryset):    
        print(_update_emp())    # in psmprj/cron.py too
    update_emp.label = "Import from SAP"  

    def update_org_func(modeladmin, request, queryset):    
        print(_update_org())    # in psmprj/cron.py too
    update_org_func.label = "Update Orgs"  

    def update_profile_func(modeladmin, request, queryset):    
        print(_update_profile())    # in psmprj/cron.py too
    update_profile_func.label = "Update Profile"  

    # fix conflict issue with two package: import/export, obj-action
    changelist_actions = ['redirect_to_export', 'redirect_to_import', 'update_emp_org_profile', 'update_emp', 'update_org_func', 'update_profile_func']
    def redirect_to_export(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_export' % self.get_model_info()))
    redirect_to_export.label = "Export"
    def redirect_to_import(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_import' % self.get_model_info()))
    redirect_to_import.label = "Import"


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
        fields = ( 'id', 'code', 'CBU', 'CBU_name', 'CBUteam', 'name', 'critical', 'outline', 
            'platform', 'os', 'db', 'lang', 'ui', 'apptype', 'no_screen', 'no_if', 'no_table', 'usertype', 'no_user',
            'operator', 'sme', 'assignment', 'assignee', 
            'grouping', 'dept', 'dept_name', 'team', 'team_name', 
            'level1', 'level2', 'initial', 'latest', 'decommission', 'remark',  
        )
       
@admin.register(GMDM)
class GMDMAdmin(DjangoObjectActions, ImportExportMixin, admin.ModelAdmin):
    resource_class = GMDMResource
    class Meta:
        model = GMDM
        import_id_fields = ('id',)    

    list_display = ('id', 'code', 'name', 'CBU','dept', 'sme', 'assignee', 'assignment', 'is_active', 'grouping')
    list_display_links = ('id', 'code', 'name')
    # list_editable = ('sme', 'assignee',  )
    readonly_fields = ('created_at', 'updated_on', 'created_by', 'updated_by', )
    search_fields = ('id', 'code', 'name')
    # autocomplete_fields = ('dept',)
    ordering = ('dept', 'team', 'code', )
    search_fields = ('id', 'code', 'name', 'outline', 'sme', 'assignee', 'assignment', 'grouping', 'ui')
    list_filter = (
        ('CBU',           RelatedDropdownFilter),
        ('operator',            DropdownFilter),
        # ('owner1__name',        DropdownFilter),   
        # ('owner2__name',        DropdownFilter),
        ('dept',          RelatedDropdownFilter),
        ('team',          RelatedDropdownFilter),
        ('critical',            DropdownFilter),
        ('apptype',             DropdownFilter),
        ('grouping',            DropdownFilter),
    )
    autocomplete_fields = ['team',  ]

    gmdm_fields = [ ('code', 'name', 'CBU', 'critical',  ),
                    ('outline','remark' ), 
                    ('platform', 'os', 'db', 'lang', 'ui','apptype'),
                    ('no_screen', 'no_if', 'no_table', 'usertype', 'no_user', ), 
                    ('operator', 'sme', 'assignment', 'assignee'),
                    ('dept', 'team', 'CBUteam'),
                    ('grouping', 'level1', 'level2'),
                    ('initial', 'latest', 'decommission'),
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
            form.base_fields['critical'].disabled = True 

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
