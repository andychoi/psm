from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CBU, Org, Team, ExtendUser

# Register your models here.
@admin.register(Div)
class DivAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name', 'head')
    pass

# Register your models here.
@admin.register(Dept)
class DeptAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'div')
    list_display_links = ('id', 'name', 'head')
    pass

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', '')
    list_display_links = ('id', 'name', 'head', 'dept', 'div')
    readonly_fields = ('created_at', 'created_by')
    pass

@admin.register(ExtendUser)
class ExtendUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'email', 'team', 'dept', 'div', 'is_active')
    list_display_links = ('user', 'name')
    search_fields = ('id', 'name', 'email')

    ordering = ('name',)

    readonly_fields = ('created_at', 'last_modified')
    fieldsets = (  # Edition form
         (None, {'fields': (('user', 'name', 'email') , ('is_external', 'is_active'), ('team',''))}),
        (_('More...'), {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                 (None, {'fields': ('user', ('name', 'email') , ('is_external', 'is_active'), ('team',''))}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        if obj.user  is not None and obj.name is None:  #default from internal user name
            obj.name = obj.user.username
        super().save_model(request, obj, form, change)

@admin.register(CBU)
class CBUAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'fullname', 'is_tier1')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', 'full_name')

    ordering = ('name',)
    list_filter = ('is_company',)
    readonly_fields = ('created_at', 'last_modified', 'created_by')
    fieldsets = (  # Edition form
#        (None, {'fields': (('name', 'is_company'), ('email', 'website'), ('phone', 'mobile'), ('address',), ('comment',))}),
         (None, {'fields': (('name', 'is_tier1', 'is_company', 'fullname', ), ('email', 'website'), ('comment',))}),
        (_('More...'), {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                (None, {'fields': (('name', 'is_tier1', 'is_company', 'fullname'), ('email', 'website'), ('comment',))}),
#                (None, {'fields': (('name', 'is_company'), ('email', 'website'), ('phone', 'mobile'), ('address',), ('comment',))}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
