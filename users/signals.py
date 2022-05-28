
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

# https://stackoverflow.com/questions/62252925/how-to-use-django-signals-using-singnals-py

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:  #user created
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    try: 
        instance.profile.save()
    except:
        pass
    
@receiver(post_save, sender=Profile)
def profile_receiver(sender, instance, created, **kwargs):
    if  created: # profile created
        pass 
    else: # profile updated 
       print("profile updated")