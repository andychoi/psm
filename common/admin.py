from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Org, Team, ExtendUser

# Register your models here.
@admin.register(Org)
class OrgAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')    
    pass

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'org')
    list_display_links = ('id', 'name')
    readonly_fields = ('created_at', 'created_by')
    pass

@admin.register(ExtendUser)
class ExtendUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'email', 'team', 'org', 'is_active')
    list_display_links = ('user', 'name')
    search_fields = ('id', 'name', 'email')

    ordering = ('name',)

    readonly_fields = ('created_at', 'last_modified')
    fieldsets = (  # Edition form
         (None, {'fields': (('user', 'name', 'email') , ('is_external', 'is_active'), ('team','org'))}),
        (_('More...'), {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                 (None, {'fields': ('user', ('name', 'email') , ('is_external', 'is_active'), ('team','org'))}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        if obj.user  is not None and obj.name is None:  #default from internal user name
            obj.name = obj.user.username
        super().save_model(request, obj, form, change)