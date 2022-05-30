
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

# https://stackoverflow.com/questions/62252925/how-to-use-django-signals-using-singnals-py

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:  #user created

        # check if same profile (email) exist
        found = Profile.objects.get(email=instance.email) if not instance.email is None else None
        if not found:    
            Profile.objects.create(user=instance, username=instance.username)

# try to create profile double time: by signal and by form.
# use get_or_create instead of create
# refer this: https://stackoverflow.com/questions/23926385/difference-between-objects-create-and-object-save-in-django-orm

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    #profile not exist
    # profile_exist = True
    if not hasattr(instance, 'profile'):
        # profile_exist = (instance.profile != None)
        try:
            found = Profile.objects.get(email=instance.email) if not instance.email is None else None
        except:
            Profile.objects.create(user=instance, username=instance.username)
            print("profile created")

    # if profile_exist: #to avoid cyclic, check create_profile
    else:
        if ( instance.profile.email != instance.email)  :
            instance.profile.email = instance.email
            instance.profile.save(update_fields=['email'])
        if ( instance.profile.is_active != instance.is_active ) : 
            instance.profile.is_active = instance.is_active
            instance.profile.save(update_fields=['is_active'])
        if not instance.profile.username:
            instance.profile.username = instance.username   #first+last
            instance.profile.save(update_fields=['username']) 


@receiver(post_save, sender=Profile)
def profile_receiver(sender, instance, created, **kwargs):
    if  created: # profile created
        pass 
    
    else: # profile updated -> user update 
        # check if user exist before processing
        try:
            # if hasattr(instance, 'user') and instance.user != None: #user exist in linked way
            changed = False
            if  instance.user.email != instance.email:
                instance.user.email = instance.email
                changed = True
            if  instance.user.is_active != instance.is_active:
                instance.user.is_active = instance.is_active
                changed = True
            if changed:
                instance.user.save()
            print("user updated")
        except Profile.DoesNotExist:
            print("user not exist!")

