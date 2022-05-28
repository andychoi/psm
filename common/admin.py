from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin

from .models import CBU, Div, Dept, Team, ExtendUser

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
    class Meta:
        model = Dept
        import_id_fields = ('id',)
        
@admin.register(Team)
class TeamAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'head', 'dept', 'div', 'is_active')
    list_display_links = ('id', 'name')
    readonly_fields = ('created_at', 'created_by')
    class Meta:
        model = Team
        import_id_fields = ('id',)

@admin.register(ExtendUser)
class ExtendUserAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'email', 'u_team', 'u_dept', 'u_div', 'is_active')
    list_display_links = ('user', 'name')
    search_fields = ('id', 'name', 'email', 'manager__name')

    ordering = ('name',)

    readonly_fields = ('created_at', 'last_modified')
    fieldsets = (  # Edition form
         (None, {'fields': (('user', 'name', 'email') , ('manager', 'is_external', 'is_active'), ('u_team','u_dept', 'u_div'), ('is_pro_reviewer','is_sec_reviewer', 'is_inf_reviewer', 'is_app_reviewer','is_mgt_reviewer',))}),
        (_('More...'), {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                 (None, {'fields': ('user', ('name', 'email') , ('manager', 'is_external', 'is_active'), ('u_team','u_dept', 'u_div'), ('is_pro_reviewer','is_sec_reviewer', 'is_inf_reviewer', 'is_app_reviewer','is_mgt_reviewer',))}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        if obj.user  is not None and obj.name is None:  #default from internal user name
            obj.name = obj.user.username
        super().save_model(request, obj, form, change)

    class Meta:
        model = ExtendUser
        import_id_fields = ('id',)

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