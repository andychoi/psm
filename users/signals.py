from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

# https://stackoverflow.com/questions/62252925/how-to-use-django-signals-using-singnals-py

# @receiver(pre_save, sender=User)
# def set_new_user_inactive(sender, instance, **kwargs):
#     if instance._state.adding is True:
#         print("Creating Inactive User")
#         instance.is_active = False
#     else:
#         print("Updating User Record")

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:  #user created

        # check if same profile (email) exist, don't link to User automatically, causing dump...
        found = None
        try:
            found = Profile.objects.get(email=instance.email) if not instance.email is None else None
        except:
            pass
        if not found:    
            Profile.objects.create(user=instance, name="%s %s" % (instance.first_name, instance.last_name) if instance.first_name else instance.username, 
                email=instance.email if instance.email else None)
        else:
            if instance.email:
                qs = Profile.objects.filter(email=instance.email)[:1]
                Profile.objects.filter(id__in=qs).update(user = instance)

# try to create profile double time: by signal and by form.
# use get_or_create instead of create
# refer this: https://stackoverflow.com/questions/23926385/difference-between-objects-create-and-object-save-in-django-orm

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    #profile not exist
    # profile_exist = True
    if kwargs['created'] == True:
        pass
    
    else:
        if not hasattr(instance, 'profile'):    #last login updating in User... triggering this
            # profile_exist = (instance.profile != None)
            try:
                found = Profile.objects.get(email=instance.email) if not instance.email is None else None
            except:
                Profile.objects.create(user=instance, name=instance.username)
                print("profile created")

        # if profile_exist: #to avoid cyclic, check create_profile
        else:
            if instance.email and ( instance.profile.email is None or ( instance.profile.email != instance.email))  :
                instance.profile.email = instance.email
                instance.profile.save(update_fields=['email'])
            if ( instance.profile.is_active != instance.is_active ) : 
                instance.profile.is_active = instance.is_active
                instance.profile.save(update_fields=['is_active'])
            if not instance.profile.name:
                instance.profile.name = instance.username   #first+last
                instance.profile.save(update_fields=['name']) 


@receiver(post_save, sender=Profile)
def profile_receiver(sender, instance, created, **kwargs):
    if  created: # profile created
        pass 
    
    else: # profile updated -> user update 
        # check if user exist before processing
        try:
            # if hasattr(instance, 'user') and instance.user != None: #user exist in linked way
            changed = False
            if hasattr(instance, 'email') and not instance.email is None and hasattr(instance.user, 'email'):                
                if  instance.user.email != instance.email:
                    instance.user.email = instance.email
                    instance.user.save(update_fields=['email'])
            if hasattr(instance, 'is_active') and hasattr(instance.user, 'is_active'):                
                if  instance.user.is_active != instance.is_active:
                    instance.user.is_active = instance.is_active
                    instance.user.save(update_fields=['is_active'])
                # print("user updated")
        except Profile.DoesNotExist:
            print("user not exist!")

