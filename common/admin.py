from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from django.contrib import messages
from import_export import resources, fields
from django.core.exceptions import ValidationError
from django.conf import settings

from .models import CompanyHoliday, CBU, Div, Dept, Team, WBS, GMDM, Employee

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
    list_display = ('id', 'name', 'head', 'is_active')
    list_display_links = ('id', 'name')
    autocomplete_fields = ('head',)
    ordering = ('id', )
    class Meta:
        model = Div
        import_id_fields = ('id',)

# Register your models here.
@admin.register(Dept)
class DeptAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'head', 'div', 'is_active', 'pm_count')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'head__name')    
    autocomplete_fields = ('head',)
    ordering = ('id', )
    class Meta:
        model = Dept
        import_id_fields = ('id',)
        
@admin.register(Team)
class TeamAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'head', 'dept', 'is_active', 'pm_count')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'head__name')
    autocomplete_fields = ('head',)
    ordering = ('id', )
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
         (None, {'fields': (('name', 'cbu_type', 'is_tier1', 'is_active'), ('fullname', 'group') , ('email', 'website'), ('comment',))}),
        (_('More...'), {'fields': (('created_at', 'updated_on') ), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('name', 'cbu_type', 'is_tier1', 'is_active'), ('fullname', 'group'), ('email', 'website'), ('comment',))}),
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

def _update_wbs():
    ret = {"E_RET": "E", "E_MSG": ""}
    timezone = pytz.timezone("America/Los_Angeles")

    if not settings.SAP:
        ret["E_MSG"] = "SAP connection is not enabled in setting"
        return ret
        
    data = {}
    with Connection(**settings.SAP_CONN_WBS) as conn:
        try:
            result = conn.call('ZPS_PROJECT_LIST', ET_TAB=[])
            for item in result['ET_TAB']:
                if item['ZZLARGE'] == 'S':
                    tObj = {}
                    tObj['PSPID'] = item['PSPID']
                    tObj['POST1'] = item['POST1']
                    tObj['SORTL'] = item['SORTL']
                    tObj['ERNAM'] = item['ERNAM_PRPS']
                    tObj['ERDAT'] = item['ERDAT_PRPS']
                    tObj['AEDAT'] = item['AEDAT_PRPS']
                    tObj['STATUS'] = item['STATUS']
                    tObj['BUDGET'] = item['BUDGET']
                    data[ tObj['PSPID'] ] = tObj
        except Exception as e:
            ret["E_MSG"] = 'RFC Error: ' + str(e)
            return ret

    try:
        for key in data.keys():
            item = data[key]
            user = None
            userSet = User.objects.filter(username=item['ERNAM'].lower())
            if len(userSet) > 0:
                user = userSet[0]
            ctime = None
            if item['ERDAT'] != '':
                ctime = datetime.strptime(item['ERDAT'], '%Y%m%d') #.strftime('%Y-%m-%d')
                ctime = timezone.localize(ctime)
            utime = None
            if item['AEDAT'] != '':
                utime = datetime.strptime(item['AEDAT'], '%Y%m%d') #.strftime('%Y-%m-%d')
                utime = timezone.localize(utime)
            wbsSet = WBS.objects.filter(wbs=item['PSPID'])
            if (len(wbsSet) > 0):
                if ctime == None:
                    ctime = wbsSet[0].created_at
                if utime == None:
                    utime = wbsSet[0].updated_on
                wbsSet.update(name = item['POST1'], cbu = item['SORTL'], status = item['STATUS'], budget = item['BUDGET'], created_by = user, created_at = ctime, updated_on = utime)
            else:
                wbs = WBS(wbs = item['PSPID'], name = item['POST1'], cbu = item['SORTL'], status = item['STATUS'], budget = item['BUDGET'], created_by = user, created_at = ctime, updated_on = utime)
                wbs.save()
    except Exception as e:
        ret["E_MSG"] = 'An error occurs during DB operations' + str(e)
        return ret
    ret["E_RET"] = 'S'
    return ret

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

    # def import_func_deprecated(modeladmin, request, queryset):
        
    #     data = {}
    #     with Connection(**settings.SAP_CONN_WBS) as conn:
    #         try:
    #             # abap_structure = {'RFCINT4': 345}
    #             # abap_table = [abap_structure]
    #             # result = conn.call('STFC_STRUCTURE', IMPORTSTRUCT=abap_structure, RFCTABLE=abap_table)
    #             # print (result)

    #             ROWS_AT_A_TIME = 200

    #             table = 'ZSUSPSV0020'
    #             fields = [ 'PSPID', 'POST1', 'SORTL', 'ERNAM_PRPS', 'ERDAT_PRPS', 'AEDAT_PRPS' ]
    #             options = [{ 'TEXT': "PSPID like 'S%'" }]

    #             rowskips = 0
    #             while True:
    #                 result = conn.call('RFC_READ_TABLE'
    #                                 , QUERY_TABLE=table
    #                                 , OPTIONS = options
    #                                 , FIELDS = fields
    #                                 , ROWSKIPS = rowskips, ROWCOUNT = ROWS_AT_A_TIME)
    #                 rowskips += ROWS_AT_A_TIME
    #                 for item in result['DATA']:
    #                     tObj = { 'STATUS': '0' }
    #                     for idx, field in enumerate(result['FIELDS']):
    #                         start = int(field['OFFSET'])
    #                         end = start + int(field['LENGTH'])
    #                         tObj[field['FIELDNAME']] = item['WA'][start:end].strip()
    #                     data[tObj['PSPID']] = tObj

    #                 if len(result['DATA']) < ROWS_AT_A_TIME:
    #                     break        

    #             table = 'ZSUSPST1000'
    #             fields = [ 'PSPID', 'STATUS' ]
    #             options = [{ 'TEXT': "PSPID like 'S%' and VERSN eq '0'" }]

    #             rowskips = 0
    #             while True:
    #                 result = conn.call('RFC_READ_TABLE'
    #                                 , QUERY_TABLE=table
    #                                 , OPTIONS = options
    #                                 , FIELDS = fields
    #                                 , ROWSKIPS = rowskips, ROWCOUNT = ROWS_AT_A_TIME)
    #                 rowskips += ROWS_AT_A_TIME
    #                 for item in result['DATA']:
    #                     tObj = {}
    #                     for idx, field in enumerate(result['FIELDS']):
    #                         start = int(field['OFFSET'])
    #                         end = start + int(field['LENGTH'])
    #                         tObj[field['FIELDNAME']] = item['WA'][start:end].strip()
    #                     if tObj['PSPID'] in data:
    #                         data[ tObj['PSPID'] ][ 'STATUS' ] = tObj[ 'STATUS' ]

    #                 if len(result['DATA']) < ROWS_AT_A_TIME:
    #                     break

    #         except Exception as e:
    #             print ('RFC error' + str(e))
    #             return

    #         try:
    #             for key in data.keys():
    #                 item = data[key]
    #                 # print(item)
    #                 # item = data['S21-0034']
    #                 # item['ERNAM_PRPS']
    #                 user = None
    #                 userSet = User.objects.filter(username=item['ERNAM_PRPS'].lower())
    #                 if len(userSet) > 0:
    #                     user = userSet[0]
    #                 ctime = None
    #                 if item['ERDAT_PRPS'] != '00000000':
    #                     ctime = datetime.strptime(item['ERDAT_PRPS'], '%Y%m%d') #.strftime('%Y-%m-%d')
    #                 utime = None
    #                 if item['AEDAT_PRPS'] != '00000000':
    #                     utime = datetime.strptime(item['AEDAT_PRPS'], '%Y%m%d') #.strftime('%Y-%m-%d')
    #                 wbsSet = WBS.objects.filter(wbs=item['PSPID'])
    #                 if (len(wbsSet) > 0):
    #                     if ctime == None:
    #                         ctime = wbsSet[0].created_at
    #                     if utime == None:
    #                         utime = wbsSet[0].updated_on
    #                     wbsSet.update(name = item['POST1'], cbu = item['SORTL'], status = item['STATUS'], created_by = user, created_at = ctime, updated_on = utime)
    #                 else:
    #                     wbs = WBS(wbs = item['PSPID'], name = item['POST1'], cbu = item['SORTL'], status = item['STATUS'], created_by = user, created_at = ctime, updated_on = utime)
    #                     wbs.save()
    #         except Exception as e:
    #             print ('DB error' + str(e))
    #             return

    #         # print(data)
    #         # pass

    # #     try:

    # #     config = ConfigParser()
    # #     config.read('sapnwrfc.cfg')
    # #     params_connection = config._sections['connection']
    # #     conn = Connection(**params_connection)

    # #     options = [{ 'TEXT': "PSPID like 'S%'"}]
    # #     fields = ['PSPID','POST1','STSPD']
    # #     pp = PrettyPrinter(indent=4)
    # #     ROWS_AT_A_TIME = 10 
    # #     rowskips = 0
    #         # while True:
    #         #     print u"----Begin of Batch---"
    #         #     result = conn.call('RFC_READ_TABLE', \
    #         #                         QUERY_TABLE = 'ZSUSPSV0020', \
    #         #                         OPTIONS = options, \
    #         #                         FIELDS = fields, \
    #         #                         ROWSKIPS = rowskips, ROWCOUNT = ROWS_AT_A_TIME)
    #         #     pp.pprint(result['DATA'])
    #         #     rowskips += ROWS_AT_A_TIME
    #         #     if len(result['DATA']) < ROWS_AT_A_TIME:
    #         #         break
    #     # except CommunicationError:
    #     #     print u"Could not connect to server."
    #     #     raise
    #     # except LogonError:
    #     #     print u"Could not log in. Wrong credentials?"
    #     #     raise
    #     # except (ABAPApplicationError, ABAPRuntimeError):
    #     #     print u"An error occurred."
    #     #     raise

    #     pass    #queryset.update(status='p')


    import_func.label = "Import from SAP"  
    import_func.short_description = "This will import WBS data from SAP system" 
    changelist_actions = ('import_func', )

from django.contrib.auth.decorators import user_passes_test


# ------------------------------------------------------------------------------------------------------------
"""A function to query SAP with RFC_READ_TABLE
"""
def sap_qry(conn, SQLTable,  Fields, Where = '', MaxRows=50, FromRow=0):
    
    # By default, if you send a blank value for fields, you get all of them
    # Therefore, we add a select all option, to better mimic SQL.
    if Fields[0] == '*':
        Fields = ''
    else:
        Fields = [{'FIELDNAME':x} for x in Fields] # Notice the format
        # pass

    # the WHERE part of the query is called "options"
    options = [{'TEXT': x} for x in Where] # again, notice the format

    # we set a maximum number of rows to return, because it's easy to do and
    # greatly speeds up testing queries.
    rowcount = MaxRows

    # Here is the call to SAP's RFC_READ_TABLE
    tables = conn.call("RFC_READ_TABLE", QUERY_TABLE=SQLTable, DELIMITER='|', FIELDS = Fields, \
                        OPTIONS=options, ROWCOUNT = MaxRows, ROWSKIPS=FromRow)

    # We split out fields and fields_name to hold the data and the column names
    fields = []
    fields_name = []

    data_fields = tables["DATA"] # pull the data part of the result set
    data_names = tables["FIELDS"] # pull the field name part of the result set

    headers = [x['FIELDNAME'] for x in data_names] # headers extraction
    long_fields = len(data_fields) # data extraction
    long_names = len(data_names) # full headers extraction if you want it

    # now parse the data fields into a list
    for line in range(0, long_fields):
        fields.append(data_fields[line]["WA"].strip())

    # for each line, split the list by the '|' separator
    fields = [x.strip().split('|') for x in fields ]

    # return the 2D list and the headers
    return fields, headers

# --------------------------------------------------------------------------------------------
def _update_emp():
    if not settings.SAP:
        logger.warning('SAP connection is not enabled in setting')
        return

    timezone = pytz.timezone(settings.TIME_ZONE)
    data = {}
    table = 'ZSUSRMT0010'
    fields = ['USER_ID', 'CREATE_DATE', 'TERMINATE_DATE', 'USER_NAME', 'EMAIL', 'COSTCENTER', 'DEPT_CODE', 'DEPT_NAME', 'CHARGE_JOB', 'POS_LEVEL', 'SUPERVISORID' ]
    where = [  ]    # "USER_ID = 'HIS10004'"    # "TERMINATE_DATE = '00000000'" ] -> terminated -> delete from current emp table  
    maxrows = 10000
    # starting row to return
    fromrow = 0

    with Connection(**settings.SAP_CONN_WBS) as conn:
        # query SAP
        results, headers = sap_qry(conn, table, fields, where, maxrows, fromrow)

    # get latest per emp_id, create_date, sort first / better to select latest... 
    sorted_results = sorted( results, key=lambda x:( x[0], x[1] ) )

    for item in sorted_results:
        if item[1][:1] == '0' or item[9].lstrip().rstrip() == '':  # invalid record, skip
            continue

        if int(item[9].lstrip().rstrip()) <= 6:
            level = 1
        elif int(item[9].lstrip().rstrip()) <= 7:
            level = 2
        else:
            level = 3
        
        # ctime = datetime(1, 1, 1, 0, 0)   # initial date/time
        cdate = timezone.localize(datetime.strptime(item[1], '%Y%m%d'))
        tdate = timezone.localize(datetime.strptime(item[2], '%Y%m%d')) if item[2][:1] != '0' else None
        email = item[4].split('@')[0].lower() 
        emp_id = item[0].lstrip().rstrip()
        if int( Employee.objects.filter(emp_id=emp_id).count() ) > 0:
                Employee.objects.filter(emp_id=emp_id).update(emp_id=emp_id, create_date=cdate, terminated=tdate, emp_name=item[3], email=email, cc=item[5], dept_code=item[6], dept_name=item[7], job=item[8], l=level, manager_id=item[10])
        else:
            Employee.objects.create(emp_id=emp_id, create_date=cdate, terminated=tdate, emp_name=item[3], email=email, cc=item[5], dept_code=item[6], dept_name=item[7], job=item[8], l=level, manager_id=item[10])

    # logger('Successfully processed...')

@user_passes_test(lambda u: u.is_superuser)
@admin.register(Employee)
class EmployeeAdmin(DjangoObjectActions, ImportExportMixin, admin.ModelAdmin):
    list_display = ('emp_id', 'emp_name', 'email', 'job', 'cc', 'l', 'dept_code', 'dept_name', 'manager_id', 'create_date', 'terminated')
    list_display_links = ('emp_id', )
    search_fields = ('emp_id', 'manager_id', 'emp_name', 'email', 'dept_name')
    ordering = ('emp_id',)

    list_filter = (
        ('terminated',  DropdownFilter),
        ('cc',          DropdownFilter),
        ('dept_name',   DropdownFilter),
        ('manager_id',  DropdownFilter),
    )

    def import_func(modeladmin, request, queryset):    
        print(_update_emp())    # in psmprj/cron.py too

    import_func.label = "Import from SAP"  

    # fix conflict issue with two package: import/export, obj-action
    changelist_actions = ['redirect_to_export', 'redirect_to_import', 'import_func']
    def redirect_to_export(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_export' % self.get_model_info()))
    redirect_to_export.label = "Export"
    def redirect_to_import(self, request, obj):
        return HttpResponseRedirect(reverse('admin:%s_%s_import' % self.get_model_info()))
    redirect_to_import.label = "Import"
# ----------------------------------------------------------------------------------------------------------------
class GMDMResource(resources.ModelResource):
    from users.models import Profile
    dept_name  = fields.Field(attribute='dept',widget=ForeignKeyWidget(model=Dept, field='name'), )
    team_name  = fields.Field(attribute='team',widget=ForeignKeyWidget(model=Team, field='name'), )
    CBU_name   = fields.Field(attribute='CBU',widget=ForeignKeyWidget(model=CBU, field='name'), )
    # owner1_name   = fields.Field(attribute='owner1',widget=ForeignKeyWidget(model=Profile, field='name'), )
    class Meta:
        model = GMDM
        fields = ( 'id', 'code', 'CBU', 'CBU_name', 'CBUteam', 'name', 'critical', 'outline', 
            'platform', 'os', 'db', 'lang', 'ui', 'no_screen', 'no_interface', 'no_table', 'usertype', 'no_user' 'apptype',
            'operator', 'sme', 'assignment', 'assignee', 
            'grouping', 'dept', 'dept_name', 'team', 'team_name', 
            'level1', 'level2', 'initial', 'latest', 'decommision', 'remark',  
        )

       
@admin.register(GMDM)
class GMDMAdmin(DjangoObjectActions, ImportExportMixin, admin.ModelAdmin):
    resource_class = GMDMResource
    class Meta:
        model = GMDM
        import_id_fields = ('id',)    

    list_display = ('id', 'code', 'name', 'CBU','dept', 'sme', 'assignee', 'assignment', 'is_active', 'grouping')
    list_display_links = ('id', 'code', 'name')
    list_editable = ('sme', 'assignee', "grouping", )
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
                    ('platform', 'os', 'db', 'lang', 'ui', 'no_screen', 'no_interface', 'no_table', 'usertype', 'no_user', 'apptype'), 
                    ('operator', 'sme', 'assignment', 'assignee'),
                    ('dept', 'team', 'CBUteam'),
                    ('grouping', 'level1', 'level2'),
                    ('initial', 'latest', 'decommision'),
                    ]
    fieldsets = (               # Edition form
        (None,  {'fields': gmdm_fields 
                , "classes": ("stack_labels",)}),
        (_('More...'), {'fields': ( ('created_at', 'updated_on'), 'created_by', ('attachment'),  ), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None): # Creation form
        return ( (None, { 'fields': self.gmdm_fields  }), )

    def is_active(self, obj):
        return "yes" if not obj.decommision else "no"

    # tip initial default version set
    def get_form(self, request, obj=None, **kwargs):
        form = super(GMDMAdmin, self).get_form(request, obj, **kwargs)
        #FIXME if read-only due to permission
        if hasattr(form, 'base_fields'):
            form.base_fields['outline'     ].widget.attrs.update({'rows':5,'cols':160})

        #permission based field read only....
        if not request.user.has_perm('admin_gmdm'):
            form.base_fields['code'].disabled = True 

        return form

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user            

    def changelist_view(self, request, extra_context=None):
        if len(request.GET) == 0:
            get_param = "is_active=True"
            return redirect("{url}?{get_parms}".format(url=request.path, get_parms=get_param))
        return super(GMDMAdmin, self).changelist_view(request, extra_context=extra_context)

    # permission... use get_form 
    # def has_change_permission(self, request, obj=None):
    #     if obj :
    #         if not request.user.has_perm('admin_gmdm'):
    #             return False    
    #         return True
    #     else:
    #         return super(GMDMAdmin, self).has_change_permission(request, obj)

    def get_queryset(self, request):
        return GMDM.objects.all()

    # validation logic
    def clean(self):
        validation_errors = {}

        # code change is only allowed for admin TODO
        # if not self.user.has_perm('admin_gmdm') and change...
        #     validation_errors['code'] = _('You are not allowed to change code')

        if len(validation_errors):
            raise ValidationError(validation_errors)
