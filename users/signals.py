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

        if getattr(instance, "email") and instance.email: 
            if not Profile.objects.filter(email=instance.email).exists():
                Profile.objects.create(user=instance, name="%s %s" % (instance.first_name, instance.last_name) if instance.first_name else instance.username, 
                    email=instance.email if instance.email else None)
            # FIXME need to check if profile with email exist, don't link to User automatically, causing dump...
            else:
                if not Profile.objects.filter(user=instance).exists() and Profile.objects.filter(email=instance.email).count() == 1:
                    Profile.objects.filter(email=instance.email).update(user = instance)

# try to create profile double time: by signal and by form.
# use get_or_create instead of create
# refer this: https://stackoverflow.com/questions/23926385/difference-between-objects-create-and-object-save-in-django-orm

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if kwargs['created'] == True:
        pass
    
    else:   #last login updating in User... triggering this
        if not hasattr(instance, 'profile'):    # if profile not exist...create it
            # found = Profile.objects.filter(email=instance.email).exists() if not instance.email is None else None
            if getattr(instance, "email") and instance.email and not Profile.objects.filter(email=instance.email).exists():
                Profile.objects.create(user=instance, name="%s %s" % (instance.first_name, instance.last_name) if instance.first_name else instance.username, 
                    email=instance.email if instance.email else None)
            else:
                Profile.objects.create(user=instance, name=instance.username)

        # if profile_exist: #to avoid cyclic, check create_profile
        else:
            if hasattr(instance, 'email') and instance.email != instance.profile.email :
                instance.profile.email = instance.email
                instance.profile.save(update_fields=['email'])

@receiver(post_save, sender=Profile)
def profile_receiver(sender, instance, created, **kwargs):
    if  created: # profile created
        pass 
    
    else: # profile updated -> user update 
        # check if user exist before processing
        if hasattr(instance, 'email') and  instance.email and hasattr(instance, 'user') and instance.user and instance.email != instance.user.email:
            instance.user.email = instance.email
            instance.user.save(update_fields=['email'])

        # except Profile.DoesNotExist:
        #     pass

