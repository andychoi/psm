from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin

from .models import CBU, Div, Dept,  WBS

# Register your models here.
@admin.register(Div)
class DivAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'head', 'is_active')
    list_display_links = ('id', 'name')
    class Meta:
        model = Div
        import_id_fields = ('id',)

# Register your models here.
@admin.register(Dept)
class DeptAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'head', 'div', 'is_active')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'head__name')    
    class Meta:
        model = Dept
        import_id_fields = ('id',)
        
# @admin.register(Team)
# class TeamAdmin(ImportExportMixin, admin.ModelAdmin):
#     list_display = ('id', 'name', 'head', 'dept', 'div', 'is_active')
#     list_display_links = ('id', 'name')
#     search_fields = ('id', 'name', 'head__name')
#     readonly_fields = ('created_at', 'created_by')
#     class Meta:
#         model = Team
#         import_id_fields = ('id',)

@admin.register(CBU)
class CBUAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'fullname', 'group', 'is_tier1')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'full_name')

    ordering = ('name',)
    list_filter = ('is_company',)
    readonly_fields = ('created_at', 'last_modified', 'created_by')
    fieldsets = (  # Edition form
#        (None, {'fields': (('name', 'is_company'), ('email', 'website'), ('phone', 'mobile'), ('address',), ('comment',))}),
         (None, {'fields': (('name', 'is_tier1', 'is_company'), ('fullname', 'group') , ('email', 'website'), ('comment',))}),
        (_('More...'), {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('name', 'is_tier1', 'is_company'), ('fullname', 'group'), ('email', 'website'), ('comment',))}),
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
    list_display = ('id', 'wbs', 'name', 'cbu', 'status', 'formatted_budget')
    list_display_links = ('wbs', 'name')
    search_fields = ('id', 'wbs', 'name')

    ordering = ('wbs',)

    readonly_fields = ('created_at', 'last_modified', 'created_by')
    fieldsets = (  # Edition form
         (None, {'fields': (('wbs', 'name', 'cbu') , ('status', 'budget'))}),
        (_('More...'), {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
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

    # Table: PROJ
    # FIELDS: PSPID, POST1, STSPD, ...

    def import_func(modeladmin, request, queryset):
    
    #     try:

    #     config = ConfigParser()
    #     config.read('sapnwrfc.cfg')
    #     params_connection = config._sections['connection']
    #     conn = Connection(**params_connection)

    #     options = [{ 'TEXT': "PSPID like 'S%'"}]
    #     fields = ['PSPID','POST1','STSPD']
    #     pp = PrettyPrinter(indent=4)
    #     ROWS_AT_A_TIME = 10 
    #     rowskips = 0
            # while True:
            #     print u"----Begin of Batch---"
            #     result = conn.call('RFC_READ_TABLE', \
            #                         QUERY_TABLE = 'ZSUSPSV0020', \
            #                         OPTIONS = options, \
            #                         FIELDS = fields, \
            #                         ROWSKIPS = rowskips, ROWCOUNT = ROWS_AT_A_TIME)
            #     pp.pprint(result['DATA'])
            #     rowskips += ROWS_AT_A_TIME
            #     if len(result['DATA']) < ROWS_AT_A_TIME:
            #         break
        # except CommunicationError:
        #     print u"Could not connect to server."
        #     raise
        # except LogonError:
        #     print u"Could not log in. Wrong credentials?"
        #     raise
        # except (ABAPApplicationError, ABAPRuntimeError):
        #     print u"An error occurred."
        #     raise

        pass    #queryset.update(status='p')


    import_func.label = "Import from SAP"  
    import_func.short_description = "This will import WBS data from SAP system" 
    changelist_actions = ('import_func', )