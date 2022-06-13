from django.contrib import admin
from .models import Profile
from django.contrib import messages
from django.contrib.auth.models import User
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
                            ('is_pro_reviewer','is_sec_reviewer', 'is_inf_reviewer', ),
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
                            ('is_pro_reviewer','is_sec_reviewer', 'is_inf_reviewer', ), 
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

    actions = ['sync_user_master']

    @admin.action(description='Migration - create User, link user with email', permissions=['change'])
    def sync_user_master(self, request, queryset):
        
        for obj in queryset:
            #check user with same email
            try:
                found = User.objects.get(email=obj.email) if not obj.email is None else None
            except:
                found = None

            if found and obj.user is None:
                # one-to-one save/update: https://stackoverflow.com/questions/70622890/how-to-assign-value-to-one-to-one-field-in-django
                # 3 methods available
                obj.user = found                  
                obj.save(update_fields=['user'])    
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
                            messages.add_message(request, messages.INFO, obj.user + ' is created to user as username: ' + obj.user.username)
                    #email as username, if not username from profile
                    elif obj.email:
                        new_user = User.objects.create_user( username=obj.email, password='init1234', email=obj.email )
                        if new_user:
                            obj.user = new_user
                            obj.save(update_fields=['user'])    
                            messages.add_message(request, messages.INFO, obj.user + ' is created to user as username: ' + obj.user.username)
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
                            messages.add_message(request, messages.INFO, obj.name + ' found in user, linked now')
                        else:
                            messages.add_message(request, messages.INFO, obj.name + ' not found in user, cannot create user without email')



    class Meta:
        model = Profile
        import_id_fields = ('id',)