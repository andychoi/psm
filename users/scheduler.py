from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
import sys
from django.contrib.auth.models import User, Group
from django.conf import settings
from .models import Profile
from psm.models import Project
from django.db.models import Count  #, F, Q, Sum, Avg

# This is the function you want to schedule - add as many as you want and then register them in the start() function below
# def deactivate_expired_accounts():
#     today = timezone.now()
#     # get accounts, expire them, etc.

# LDAP login -> create User with Staff status, but fail to assign groups... FIXME
def assign_staff_role():
    for u in User.objects.all():
        if u.is_staff == True:
            if not u.groups.all().filter(name=settings.DEFAULT_AUTH_GROUP).exists():    
                try:
                    user_group = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
                except:
                    continue    
                u.groups.add(user_group) 
        else:
            if u.groups.all().filter(name=settings.DEFAULT_AUTH_GROUP).exists():    
                u.groups.remove(u.groups.get(name=settings.DEFAULT_AUTH_GROUP)) 

def project_pm_count():
    # queryset count groupby
    pm_qs = Project.objects.values('pm').annotate(pm_count=Count('pk'))
    cbupm_qs = Project.objects.values('CBUpm').annotate(pm_count=Count('pk'))

    for item in pm_qs:
        Profile.objects.filter(id=item['pm']).update(pm_count=item['pm_count'])
    for item in cbupm_qs:
        Profile.objects.filter(id=item['CBUpm']).update(pm_count=item['pm_count'])
    # for k, v in pm_dict.items():


# https://github.com/jcass77/django-apscheduler
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # trigger=CronTrigger(second="*/10"),  # Every 10 seconds
    # run this job every 24 hours
    # scheduler.add_job(deactivate_expired_accounts, 'interval', hours=24, id='clean_accounts', jobstore='default', replace_existing=True,)
    scheduler.add_job(assign_staff_role, 'interval', hours=24, id='assign_staff_role', jobstore='default', replace_existing=True,)
    scheduler.add_job(project_pm_count, 'interval', hours=24, id='project_pm_count', jobstore='default', replace_existing=True,)

    register_events(scheduler)
    scheduler.start()
    # print("Scheduler started...", file=sys.stdout)