from django.contrib import messages
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
import sys
from django.contrib.auth.models import User, Group
from django.conf import settings
from users.models import Profile
from django.core.management import call_command
from psm.models import Project
from common.models import Dept, Team
from django.db.models import Q
from django.db.models import Count  #, F, Q, Sum, Avg
from common.dates import previous_business_day
from reports.models import Report
from common.codes import PHASE_WORK, PHASE_OPEN, Phase, State, STATE_OPEN
from psmprj.utils.mail import send_mail_async as send_mail
import logging
logger = logging.getLogger(__name__)


# This is the function you want to schedule - add as many as you want and then register them in the start() function below
# def deactivate_expired_accounts():
#     today = timezone.now()
#     # get accounts, expire them, etc.

# -----------------------------------------------------------------------------------
def database_backup():
    try:
        call_command('dbbackup')
        print("backup started...", file=sys.stdout)
    except:
        pass

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
    
    dept_qs = Project.objects.values('dept').filter(year = date.today().year).annotate(pm_count=Count('pk'))
    team_qs = Project.objects.values('team').filter(year = date.today().year).annotate(pm_count=Count('pk'))

    for item in pm_qs:
        Profile.objects.filter(id=item['pm']).update(pm_count=item['pm_count'])
    for item in cbupm_qs:
        Profile.objects.filter(id=item['CBUpm']).update(pm_count=item['pm_count'])

    for item in dept_qs:
        Dept.objects.filter(id=item['dept']).update(pm_count=item['pm_count'])
    for item in team_qs:
        Team.objects.filter(id=item['team']).update(pm_count=item['pm_count'])

    # for k, v in pm_dict.items():

def project_backfill_dates():
    for p in Project.objects.filter(year = date.today().year):
        if not p.p_launch and p.p_close:
            p.p_launch = previous_business_day(p.p_close, 1)
            p.save()    #update_fields='p_launch')   error...why?
        # if not p.p_plan_e and p.p_design_b:
        #     p.p_plan_e = previous_business_day(p.p_design_b, 1)
        #     p.save()    #update_fields='p_plan_e')
        if not p.p_design_e and p.p_uat_b:
            p.p_design_e = previous_business_day(p.p_uat_b, 1)
            p.save()    #update_fields='p_design_e')
        if not p.p_uat_e and p.p_launch:
            p.p_uat_e = previous_business_day(p.p_launch, 1)
            p.save()    #update_fields='p_uat_e')

def project_creator_from_pm():
    for p in Project.objects.all():
        if hasattr(p.pm, 'user') and p.pm.user and p.created_by != p.pm.user:
            p.created_by = p.pm.user
            p.save()    #update_fields='p_launch')   error...why?

def project_state_from_progress():
    # for p in Project.objects.filter(Q(progress=100) & ( Q(phase__in=PHASE_OPEN) | Q(state__in=STATE_OPEN))):
    for p in Project.objects.filter(progress=100).filter(Q(phase__in=PHASE_OPEN) | Q(state__in=STATE_OPEN)):
        p.phase = Phase.CLOSED.value
        p.state = State.DONE.value
        p.save()    

def late_reminder():
    for p in Project.objects.filter(year=datetime.today().year, phase__in=PHASE_WORK):
        r = Report.objects.filter(project=p).order_by('created_at').first()
        reqdt = r.created_at if r else p.p_plan_b   #p.p_kickoff if p.p_kickoff else p.p_plan_b
        date_delta = (date.today() - reqdt).days
        if date_delta > 10:

            vals = {
                "id": p.id,
                "pjcode": p.pjcode,
                "pm": str(p.pm),
                "lstrpt": p.lstrpt,
                "title": p.title,
                'plan_start': p.p_plan_b,
                "url": f'{settings.APP_URL}/project/{p.id}/',
                "sign": settings.SITE_HEADER,
            }
            email_template = settings.PSM_EMAIL_REPORT_REMINDER
            if settings.EMAIL_DEV:
                email_receiver = [ settings.EMAIL_PSM_ADMIN ]   
            else:
                email_receiver = [ p.pm.email if p.pm else p.dept.head.profile.email if p.dept.head else settings.EMAIL_PSM_ADMIN ]
                if p.dept.head:
                    email_receiver.append(p.dept.head.profile.email) 
            try:
                send_mail(
                    f'{settings.EMAIL_SUBJECT_PREFIX} Project status report reminder -{p}',
                    email_template.format(**vals),
                    settings.APP_EMAIL,
                    email_receiver,
                )
            except Exception as e:
                logger.warning("[Project #%s] Error trying to send the Project creation email - %s: %s",
                               p.pk, e.__class__.__name__, str(e))

def wbs_import():
    from common.admin import _update_wbs
    _update_wbs()

# https://github.com/jcass77/django-apscheduler
# https://apscheduler.readthedocs.io/en/latest/userguide.html
# https://pythonlang.dev/repo/jcass77-django-apscheduler/
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # trigger=CronTrigger(second="*/10"),  # Every 10 seconds
    # run this job every 24 hours
    # scheduler.add_job(deactivate_expired_accounts, 'interval', hours=24, id='clean_accounts', jobstore='default', replace_existing=True,)
    scheduler.add_job(assign_staff_role, 'interval', days=1, id='assign_staff_role', jobstore='default', replace_existing=True,)
    scheduler.add_job(project_pm_count, 'interval', weeks=1, start_date='2022-06-30', end_date='2022-06-30', id='project_pm_count', jobstore='default', replace_existing=True,)
    scheduler.add_job(project_backfill_dates, 'interval', start_date='2022-06-30', end_date='2022-06-30', weeks=2, id='project_backfill_dates', jobstore='default', replace_existing=True,)
    scheduler.add_job(late_reminder, 'interval', weeks=2, id='late_reminder', jobstore='default', replace_existing=True,)
    scheduler.add_job(project_state_from_progress, 'interval', weeks=52, start_date='2022-06-30', end_date='2022-06-30', id='project_state_from_progress', jobstore='default', replace_existing=True,)
    scheduler.add_job(database_backup, 'interval', days=1, id='database_backup', jobstore='default', replace_existing=True,)
    scheduler.add_job(wbs_import, 'interval', days=1, id='wbs_import', jobstore='default', replace_existing=True,)
    scheduler.add_job(project_creator_from_pm, 'interval', days=365, start_date='2022-06-30', end_date='2022-06-30', id='project_creator_from_pm', jobstore='default', replace_existing=True,)

    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...", file=sys.stdout)