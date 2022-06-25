from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from django.contrib import messages

from .models import CBU, Div, Dept, Team, WBS

from django.contrib.auth.models import Permission
from django.contrib import admin

from datetime import datetime
from pyrfc import Connection
from django.conf import settings
from django.utils import timezone
from users.models import User
import pytz

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
    class Meta:
        model = Dept
        import_id_fields = ('id',)
        
@admin.register(Team)
class TeamAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'head', 'dept', 'is_active', 'pm_count')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'head__name')
    autocomplete_fields = ('head',)
    class Meta:
        model = Team
        import_id_fields = ('id',)

@admin.register(CBU)
class CBUAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'fullname', 'group', 'is_tier1', 'cbu_type')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'full_name')

    ordering = ('name',)
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

@admin.register(WBS)
class WBSAdmin(DjangoObjectActions, ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'wbs', 'name', 'is_sub', 'cbu', 'status', 'formatted_budget')
    list_display_links = ('wbs', 'name')
    search_fields = ('id', 'wbs', 'name')

    ordering = ('wbs',)

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
        timezone = pytz.timezone("America/Los_Angeles")

        if not settings.SAP:
            messages.warning(request, "SAP connection is not enabled in setting")
            return
            
        data = {}
        with Connection(**settings.SAP_CONN_WBS) as conn:
            try:
                result = conn.call('ZPS_PROJECT_LIST', ET_TAB=[])
                for item in result['ET_TAB']:
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
                print ('RFC Error: ' + str(e))

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
            print ('DB error' + str(e))
            return                


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