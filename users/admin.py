from django.contrib import admin
from .models import Profile

from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from common.models import CBU, Div, Dept, Team


# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user')
#     list_display_links = ('id', 'user')
#     list_filter = ('user', )
#     list_per_page = 20
# admin.site.register(Profile, ProfileAdmin)



@admin.register(Profile)
class ProfileAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'email', 'u_team', 'u_dept', 'u_div', 'is_active')
    list_display_links = ('user', 'name')
    search_fields = ('id', 'name', 'email', 'manager__name')
    ordering = ('name',)
    readonly_fields = ('created_on', 'created_by', 'updated_on', 'updated_by')

    fieldsets = (  # Edition form
         (None, {'fields': (('user', 'name', 'email') , ('manager', 'is_external', 'is_active'), ('u_team','u_dept', 'u_div'), ('is_pro_reviewer','is_sec_reviewer', 'is_inf_reviewer', 'is_app_reviewer','is_mgt_reviewer',), ('image',), )}),
        (_('More...'), {'fields': (('created_on', 'created_by'), ('updated_on', 'updated_by')), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                 (None, {'fields': ('user', ('name', 'email') , ('manager', 'is_external', 'is_active'), ('u_team','u_dept', 'u_div'), ('is_pro_reviewer','is_sec_reviewer', 'is_inf_reviewer', 'is_app_reviewer','is_mgt_reviewer',), ('image',))}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        if obj.user  is not None and obj.name is None:  #default from internal user name
            obj.name = obj.user.username
        super().save_model(request, obj, form, change)

    class Meta:
        model = Profile
        import_id_fields = ('id',)