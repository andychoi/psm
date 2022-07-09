from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from adminfilters.multiselect import UnionFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter, ChoiceDropdownFilter
from django.http import HttpResponseRedirect
from django.urls import reverse
from import_export.admin import ImportExportMixin

# Register your models here.
from .models import WBS, Employee



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
from sap.functions import _update_wbs, _update_emp, _update_org, _update_profile, _update_emp_org_profile

@user_passes_test(lambda u: u.is_superuser)
@admin.register(Employee)
class EmployeeAdmin(DjangoObjectActions, ImportExportMixin, admin.ModelAdmin):
    list_display = ('emp_id', 'emp_name', 'email', 'job', 'cc', 'l', 'dept_code', 'dept_name', 'manager_id', 'create_date', 'terminated', 'updated_on')
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

