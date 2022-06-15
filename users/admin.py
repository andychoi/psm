from django.contrib import admin
from .models import Profile
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from django_object_actions import DjangoObjectActions
from adminfilters.multiselect import UnionFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter, ChoiceDropdownFilter

from common.models import CBU, Div, Dept

#for RAW query
# from django.db import connection

@admin.register(Profile)
class ProfileAdmin(ImportExportMixin, admin.ModelAdmin):
    # list_display = ('id', 'user', 'name', 'email', 'dept', 'manager', 'u_div', 'CBU', 'is_active')
    list_display = ('id', 'user', 'name', 'email', 'dept', 'CBU', 'is_active')
    list_display_links = ('id', 'user', 'name')
    search_fields = ('id', 'name', 'email', 'CBU__name', 'user__id', 'user__username') #, 'manager__name') -> dump... why? circular??
    ordering = ('CBU', 'dept', 'team', 'name',)
    readonly_fields = ('created_on', 'created_by', 'updated_on', 'updated_by')
    autocomplete_fields = ( 'user', 'team')
    fieldsets = (  # Edition form
         (None, {'fields': (('user', 'name', 'email') , ('manager', 'is_psmadm', 'is_active'), 
                            # ('team','dept', 'u_div'), 
                            ('dept', 'team'), 
                            ('is_external', 'CBU',), 
                            # ('is_pro_reviewer','is_sec_reviewer', 'is_inf_reviewer', 'is_app_reviewer','is_mgt_reviewer',),
                            ('is_pro_reviewer', ),
                            # ('image',), 
                            )}),
        (_('More...'), {'fields': (('created_on', 'created_by'), ('updated_on', 'updated_by')), 'classes': ('collapse',)}),
    )
    list_filter = (
        ('CBU', RelatedDropdownFilter),
        ('dept', RelatedDropdownFilter),
        ('team', RelatedDropdownFilter),
        'is_active'
    )
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (      # Creation form
                 (None, {'fields': ('user', ('name', 'email') , ('manager', 'is_psmadm', 'is_active'), 
                            # ('team','dept', 'u_div'), 
                            ('dept', 'team' ), 
                            ('is_external', 'CBU' ), 
                            ('is_pro_reviewer', ), 
                            # ('is_pro_reviewer','is_sec_reviewer', 'is_inf_reviewer', 'is_app_reviewer','is_mgt_reviewer',), 
                            # ('image',), 
                            ('id_auto') )}),
            )
        return fieldsets

    # object-function
    # def email_test(self, request, obj):
    #     from psmprj.utils.mail import send_mail_async as send_mail
    #     no_mails = send_mail(
    #         subject='Subject here',
    #         message='Here is the message.',
    #         html_message="<h1>Here is title</h1>",
    #         from_email='postmaster@sandbox8d3a1fef491c445da7a28136096d4050.mailgun.org',
    #         recipient_list=['choibc9@gmail.com'],
    #         fail_silently=False,
    #     )
    #     messages.add_message(request, messages.INFO, '%s emails sent!' % no_mails)

    # email_test.label = "Email Test"  
    # change_actions = ('email_test', )

    # conflict import/export: changelist_actions = ('email_test', )    

    # validation check
    def clean(self):
        if not self.email and not User.objects.filter(email=self.email).exists():
            raise ValidationError("Email is already registered in User table")

    # use signals.py to sync between User and Profile        
    # def save_model(self, request, obj, form, change):
        # if change is False:     # create
        #     obj.created_by = request.user
        # super().save_model(request, obj, form, change)

    actions = ['sync_user_master', 'set_staff', 'remove_staff']

    @admin.action(description='Set as staff', permissions=['change'])
    def set_staff(self, request, queryset):
        for obj in queryset:
            if obj.user:
                User.objects.filter(id=obj.user.id).update(is_staff=True)
                try:
                    user_group = Group.objects.get(name='staff')
                    obj.user.groups.add(user_group) 
                except:
                    pass    

    @admin.action(description='Remove from staff', permissions=['change'])
    def remove_staff(self, request, queryset):
        for obj in queryset:
            if obj.user:
                User.objects.filter(id=obj.user.id).update(is_staff=False)
                try:
                    user_group = Group.objects.get(name='staff')
                    obj.user.groups.remove(user_group) 
                except:
                    pass    

    @admin.action(description='Migration - create User, link user with email', permissions=['change'])
    def sync_user_master(self, request, queryset):
        
        for obj in queryset:
            if obj.email is None or obj.email == "":
                messages.add_message(request, messages.ERROR, '%s - %s has no email address to create user' % (obj.id, obj.name))
                break

            #check user with same email
            if Profile.objects.filter(email = obj.email).count() > 1:
                messages.add_message(request, messages.ERROR, '%s - %s has multiple profiles with same email' % (obj.id, obj.name))
                break

            try:
                found = User.objects.get(email=obj.email) if not obj.email is None else None
            except:
                found = None

            if found and obj.user is None:
                # one-to-one save/update: https://stackoverflow.com/questions/70622890/how-to-assign-value-to-one-to-one-field-in-django
                # 3 methods available
                obj.user = found                  
                obj.save(update_fields=['user'])    # duplicate update....
                # Profile.objects.filter(pk=obj.id).update(user=found)   #method 2
                # with connection.cursor() as cursor:                    #method 3
                #     cursor.execute("UPDATE users_profile SET user_id = %s WHERE id = %s", ( found.id, obj.id ) )
                                
                messages.add_message(request, messages.INFO, obj.name + 'is linked with user using email')

            elif not found and obj.user is None:
                user_with_email = False
                try:
                    found = User.objects.get(username=obj.email) if not obj.email is None else None
                except:
                    found = None

                if found:
                    obj.user = found
                    obj.save(update_fields=['user'])    
                    messages.add_message(request, messages.INFO, obj.name + ' already exists with email address as username: ' + obj.email)
                else:
                    if obj.migrated:
                        new_user = User.objects.create_user( username=obj.migrated.lower(), password='init1234', email=obj.email )
                        if new_user:
                            obj.user = new_user
                            obj.save(update_fields=['user'])    
                            messages.add_message(request, messages.INFO, '%s is created to user as username: %s' % (obj.name, obj.user.username))
                    #email as username, if not username from profile
                    elif obj.email:
                        new_user = User.objects.create_user( username=obj.email, password='init1234', email=obj.email )
                        if new_user:
                            obj.user = new_user
                            obj.save(update_fields=['user'])    
                            messages.add_message(request, messages.INFO, '%s is created to user as username: %s ' % (obj.name, obj.user.username))
                    else:
                        # causing duplicate key... signal User -> Profile (different username) -> don't create
                        # username = obj.username.lower().replace(" ", "").replace(",",".")
                        # user = User.objects.create_user( username=username, password='demo' )
                        try:
                            found = User.objects.get( username=obj.name )
                        except:
                            found = None
                        if found:
                            obj.user = found
                            obj.save(update_fields=['user'])    
                            messages.add_message(request, messages.INFO, '%s found in user, linked now' % obj.name)
                        else:
                            messages.add_message(request, messages.INFO, '%s not found in user, cannot create user without email' % obj.name)

    # permission check; 
    # def has_change_permission(self, request, obj=None):
    #     if obj :
    #         if obj.field == value and not request.user.has_perm('admin'):
    #             return False    # You do not have access to version 21 (Unplanned approved') 
    #         return True
    #     else:
    #         return super(ProjectPlanAdmin, self).has_change_permission(request, obj)

    # object level permission: https://www.youtube.com/watch?v=2jhQyWeEVHc&ab_channel=VeryAcademy
    # model level permission:  https://www.youtube.com/watch?v=wlYaUvfXJDc&ab_channel=VeryAcademy
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)        
        # is_superuser = request.user.is_superuser
        
        if form.base_fields and not request.user.has_perm('users.admin_profile'):
            # when creating or updating by non-reviewer (except superuser)
            # allow only reviewer to allow updating
            form.base_fields['is_psmadmin'].disabled = True 
            form.base_fields['is_pro_reviewer'].disabled = True 

        return form

    class Meta:
        model = Profile
        import_id_fields = ('id',)