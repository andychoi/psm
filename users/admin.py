from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from import_export.admin import ImportExportMixin
from django_object_actions import DjangoObjectActions
from adminfilters.multiselect import UnionFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter, ChoiceDropdownFilter
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.html import mark_safe
from django.urls import reverse
from common.models import CBU, Div, Dept
from psm.models import Project

from .models import Profile, ProfileCBU

#for RAW query
# from django.db import connection
# @admin.register(Profile)
# class ProfileAdmin(ImportExportMixin, admin.ModelAdmin):
#     list_display = ('proxy_name', 'id', 'user', 'name', 'email', 'dept', 'CBU', 'pm_count')
#     search_fields = ('id', 'name', 'email', 'CBU__name', 'user__id', 'user__username') #, 'manager__name') -> dump... why? circular??
#     list_display_links = ('id', 'name', 'email')
"""

https://stackoverflow.com/questions/31430241/how-to-remove-the-functionality-of-changelist-filter-appearing-in-django-admin
Example:
from django.contrib.auth.admin import UserAdmin
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_filter = ()

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        return qs.filter(is_staff=True)

"""
class ProfileResource(resources.ModelResource):
    cbu_names       = fields.Field(attribute='CBU',    widget=ManyToManyWidget(model=CBU, separator=',', field='name'), )
    class Meta:
        model = Profile
        fields = ( 'id', 'user', 'user__username', 'name', 'email', 'wcal', 'dept__name', 'team__name', 'cbu_names', 
                   'auto_id', 'manager', 'department', 'usertype', 'notes', 'pm_count', 'proxy_name'
        )
        export_order = fields

@admin.register(Profile)
class ProfileAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = ProfileResource

    # list_display = ('id', 'user', 'name', 'email', 'dept', 'manager', 'u_div', 'CBU', 'is_active')
    list_display = ('id', 'user', 'name', 'email', 'wcal', 'dept', 'team', 'is_active', 'is_staff', 'pm_count_link', 'goto_user', 'cbu_names', 'auto_id', 'updated_on', 'usertype', 'proxy_name', )
    list_display_links = ('id', 'name', 'email')
    list_editable = ( 'wcal',)
    search_fields = ('id', 'name', 'email', 'auto_id', 'CBU__name', 'user__id', 'user__username') #, 'manager__name') -> dump... why? circular??
    ordering = ('CBU__id', 'dept', 'team', 'name', )
    readonly_fields = ('created_at', 'created_by', 'updated_on', 'updated_by', 'auto_id', 'manager', 'department', 'job')
    autocomplete_fields = ( 'user', 'team', 'CBU' )
    fieldsets = (  # Edition form
         (None, {'fields': (('user', 'name',), ('email',) , ('CBU',), ('usertype', 'is_psmadm', ), 
                            ('wcal', 'dept', 'team'), 
                            ('notes', ),
                            ('auto_id', 'manager', 'department', 'job',  ), #'job', 'mobile', ),
                            # ('image',), 
                            )}),
        (_('More...'), {'fields': (('created_at', 'created_by'), ('updated_on', 'updated_by', 'proxy_name', )), 'classes': ('collapse',)}),
    )
    list_filter = (
        ('CBU',  RelatedDropdownFilter),
        ('dept', RelatedDropdownFilter),
        ('team', RelatedDropdownFilter),
        ('usertype', DropdownFilter),
        ('pm_count', DropdownFilter),
        'user__is_staff',
        'user__is_active',
        'proxy_name',
        ('wcal', DropdownFilter),
    )
    # tip hide/show changelist-filter https://stackoverflow.com/questions/6086651/minimize-the-list-filter-in-django-admin#answer-6298648
    # https://stackoverflow.com/questions/6264823/trying-to-show-hide-the-change-list-filter-in-django-admin
    # class Media:
    #     js = ['js/list_filter_collapse.js']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                 (None, {'fields': ('user', ('name',), ('email'), ('CBU',), ('usertype', 'is_psmadm', ), 
                            ('wcal', 'manager', 'dept', 'team', 'job',   ), 
                            ('notes' ), 
                        )}),
            )
        return fieldsets

    def is_active(self, obj):
        return obj.user.is_active   if not obj.user is None else False
    def is_staff(self, obj):
        return obj.user.is_staff    if not obj.user is None else False
    # def pm_count(self, obj):
    #     return Project.objects.filter(pm=obj).count()

    # def changelist_view(self, request, extra_context=None):
    #     if len(request.GET) == 0:
    #         get_param = "CBU__id__exact=50"
    #         return redirect("{url}?{get_parms}".format(url=request.path, get_parms=get_param))
    #     return super(ProfileEmpAdmin, self).changelist_view(request, extra_context=extra_context)           

    #README: https://django-tips.avilpage.com/en/latest/admin_custom_admin_actions.html

    def pm_count_link(self, obj):
        # FIXME
        # url = reverse('admin:psm_project') + f'?pm={[obj.id]}'
        return mark_safe(f"<a href='{reverse('admin:psm_project_changelist')}?pm={obj.id}'>{obj.pm_count}</a>")
    pm_count_link.short_description = 'PM count'

    #object-function
    def goto_user(self, obj):
        if obj.user:
            return mark_safe(f"<a class='btn btn-outline-success p-1 btn-sm adminlist' style='color:#000' target='_blank' href='/admin/auth/user/{obj.user.pk}/change'>Goto Auth</a>")
    goto_user.short_description = 'Auth'

    # conflict import/export: changelist_actions = ('email_test', )    

    # validation check
    def clean(self):
        if not self.email and not User.objects.filter(email=self.email).exists():
            raise ValidationError("Email is already registered in User table")

    # use signals.py to sync between User and Profile        
    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)

    actions = ['update_pm_count', 'sync_user_master', 'set_staff', 'remove_staff']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions and not request.user.is_superuser :
            del actions['delete_selected']
        return actions

    @admin.action(description='Set as staff', permissions=['change'])
    def set_staff(self, request, queryset):
        user_group = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
        for obj in queryset:
            if obj.user:
                User.objects.filter(id=obj.user.id).update(is_staff=True)
                try:
                    obj.user.groups.add(user_group) 
                except:
                    pass    

    @admin.action(description='Remove from staff', permissions=['change'])
    def remove_staff(self, request, queryset):
        user_group = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
        for obj in queryset:
            if obj.user:
                User.objects.filter(id=obj.user.id).update(is_staff=False)
                try:
                    obj.user.groups.remove(user_group) 
                except:
                    pass    

    def create_user(self, request, obj):
        try:
            User.objects.get( username=obj.auto_id if obj.auto_id else obj.email )
        except User.DoesNotExist:
            new_user = User.objects.create_user( username=obj.auto_id if obj.auto_id else obj.email, email=obj.email )
            if new_user:
                obj.user = new_user
                obj.save(update_fields=['user'])    
                messages.add_message(request, messages.INFO, '%s is created to user as username: %s ' % (obj.name, obj.user.username))

    def link_user(self, request, obj, link):
        try:
            Profile.objects.get(user=link)
        except User.DoesNotExist:  #check if found user is linked to other profile
            obj.user = link                  
            obj.save(update_fields=['user'])    # duplicate update....
            messages.add_message(request, messages.INFO, obj.name + 'is linked with user using email')

    @admin.action(description='Migration - create User, link user with email', permissions=['change'])
    def sync_user_master(self, request, queryset):
        # email is required for django user creation
        for obj in queryset:
            if obj.user:
                continue
            if obj.email is None or obj.email.strip() == "":
                messages.add_message(request, messages.WARNING, obj.name + ' has no valid email address in profile')
                continue
            if Profile.objects.filter(email = obj.email).count() > 1:  #if multiple profiles with same email, pass
                continue

            found = None
            try:
                found = User.objects.get(email=obj.email)
            except User.DoesNotExist:
                pass    # create user 
            except User.MultipleObjectsReturned:
                messages.add_message(request, messages.WARNING, obj.name + ' has multiple User with email in profile')
                continue

            if found:
                self.link_user(request, obj, found)
            else:
                self.create_user(request, obj)



    # permission check; 
    # def has_change_permission(self, request, obj=None):
    #     if obj :
    #         if obj.field == value and not request.user.has_perm('admin'):
    #             return False    # You do not have access to version 21 (Unplanned approved') 
    #         return True
    #     else:
    #         return super(ProjectRequestAdmin, self).has_change_permission(request, obj)

    # object level permission: https://www.youtube.com/watch?v=2jhQyWeEVHc&ab_channel=VeryAcademy
    # model level permission:  https://www.youtube.com/watch?v=wlYaUvfXJDc&ab_channel=VeryAcademy
    
    # @admin.action(description='Update PM count')
    # def update_pm_count(self, request, queryset): -> scheduler

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)        
        if request.user.is_superuser or request.user.profile.is_psmadm:
            return form

        # field level permission 
        # for complex rule, let's implement https://github.com/dfunckt/django-rules         
        # if form.base_fields and not request.user.has_perm('users.admin_profile'):

        # allow own profile edit
        if form.base_fields and ( request.user.is_staff or request.user.profile == obj):
            # tip dict attribute for loop set
            for k,v in form.base_fields.items():
                v.disabled = True
            # when creating or updating allow to staff (except superuser)
            # allow only reviewer to allow updating
            form.base_fields['wcal'].disabled = False 
            form.base_fields['dept'].disabled = False 
            form.base_fields['team'].disabled = False 
            form.base_fields['name'].disabled = False 

        # default display only
        elif form.base_fields:
            for k,v in form.base_fields.items():
                v.disabled = True


        return form

    class Meta:
        model = Profile
        import_id_fields = ('id',)


class ProfileCBUResource(resources.ModelResource):
    cbu_names       = fields.Field(attribute='CBU',    widget=ManyToManyWidget(model=CBU, separator=',', field='name'), )
    class Meta:
        model = ProfileCBU
        fields = ( 'id', 'user', 'user__username', 'name', 'email', 'cbu_names', 'auto_id', 'notes', 'pm_count'
        )
        export_order = fields

# ------------------------------------------------------------------
@admin.register(ProfileCBU)
class ProfileCBUAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = ProfileCBUResource
    # list_display = ('id', 'user', 'name', 'email', 'dept', 'manager', 'u_div', 'CBU', 'is_active')
    list_display = ('id', 'user', 'name', 'email', 'cbu_names', 'pm_count')
    list_display_links = ('id', 'user', 'name')
    search_fields = ('id', 'name', 'email', 'CBU__name', 'user__id', 'user__username') #, 'manager__name') -> dump... why? circular??
    ordering = ('CBU', 'name', )
    readonly_fields = ('created_at', 'created_by', 'updated_on', 'updated_by')
    autocomplete_fields = ( 'user', 'CBU'  )
    fieldsets = (  # Edition form
         (None, {'fields': (('name', 'email', ) ,
                            ('CBU', 'is_external', 'notes' ),
                            )}),
        (_('More...'), {'fields': (('created_at', 'created_by'), ('updated_on', 'updated_by'), ('user',)), 'classes': ('collapse',)}),
    )
    list_filter = (
        ('CBU', RelatedDropdownFilter),
    )
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                 (None, {'fields': (('name', 'email',  ) , 
                            ('CBU', 'is_external', 'notes' ), 
                        )}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)
        
    # move to batch scheduler
    # actions = ['update_pm_count', ]
    # @admin.action(description='Update PM count')
    # def update_pm_count(self, request, queryset):
    #     for obj in queryset:
    #         obj.pm_count = Project.objects.filter(CBUpm=obj).count()
    #         obj.save()        

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions and not request.user.is_superuser :
            del actions['delete_selected']
        return actions
