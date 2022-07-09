# common/functions.py
# emp, org, profile functions

from django.contrib.auth.models import User, Group
from datetime import datetime, date
from django.conf import settings
from django.db.models import Count, F, Q 
import pytz
from pyrfc import Connection

from .sap import sap_qry, get_sap_emp_data

from users.models import Profile
from common.models import CBU, Div, Dept, Team
from sap.models import Employee, WBS

# ------------------------------------------------------------------------------------------------------------
import logging
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------------
def _update_org():
    timezone = pytz.timezone(settings.TIME_ZONE)
    updated_on = timezone.localize(datetime.now())

    # create/update div,dept,team / caution in filter - date=None 
    org_list = Employee.objects.filter(Q(terminated__isnull=True)).values('l', 'dept_name').annotate(emp_count=Count('emp_id')).order_by('l')
    cc_list = Employee.objects.filter(Q(terminated__isnull=True)).values('l', 'dept_name', 'cc').annotate(emp_count=Count('emp_id')).order_by('l')
    mgr_list = Employee.objects.filter(Q(terminated__isnull=True) & Q(l=3)).values('l', 'manager_id').annotate(emp_count=Count('emp_id')).order_by('l')

    new_upd_team, new_upd_dept, new_upd_div = [], [], [] 
    for org in org_list:
        # one HR org may have multiple cc, first 'cc' is taken... / reset head and org hierarchy
        cc = cc_list.filter(l=org['l'], dept_name__exact=org['dept_name'])[0]
        if org['l'] == 3:
            obj, created = Team.objects.update_or_create(name = org['dept_name'], defaults = {'em_count':org['emp_count'], 'cc':cc['cc'], 'is_active':True, 'head': None, 'dept': None })
            # if created:
            new_upd_team.append(obj.id)
        elif  org['l'] == 2:
            obj, created = Dept.objects.update_or_create(name = org['dept_name'], defaults = {'em_count':org['emp_count'], 'cc':cc['cc'], 'is_active':True, 'head': None, 'div': None })
            new_upd_dept.append(obj.id)
        elif  org['l'] == 1:
            obj, created = Div.objects.update_or_create(name = org['dept_name'], defaults = {'em_count':org['emp_count'], 'cc':cc['cc'], 'is_active':True, 'head': None })
            new_upd_div.append(obj.id)

    # add 'virtual' dept for team if report to is div level                
    for m in mgr_list:
        manager = Employee.objects.get(emp_id=m['manager_id'])
        try:
            mgr_profile = Profile.objects.get(auto_id__exact=manager.emp_id)
        except:
            mgr_profile = None
        if manager.l == 1:
            obj, created = Dept.objects.update_or_create(name = manager.dept_name, 
                defaults = {'em_count':m['emp_count'], 'cc':manager.cc, 'head': mgr_profile, 'div': None, 'is_active':True, 'is_virtual':True })
            new_upd_dept.append(obj.id)

    # disable inactive orgs
    for o in Team.objects.exclude(id__in=new_upd_team):
        Team.objects.filter(id=o.id).update(is_active=False, em_count=0)
    for o in Dept.objects.exclude(id__in=new_upd_dept):
        Dept.objects.filter(id=o.id).update(is_active=False, em_count=0)
    for o in Div.objects.exclude(id__in=new_upd_div):
        Div.objects.filter(id=o.id).update(is_active=False, em_count=0)

    #TODO
    # create/update profile and assign div, dept, team
    # update head for div,dept,team 

    # logger('Successfully processed...')

def _update_profile():

    e_list = Employee.objects.all()
    
    for e in e_list:
        if e.terminated:
            User.objects.filter(username=e.emp_id).update(is_active=False, is_staff=False)
        
        else:
            mgr  = _get_mgr(e.manager_id)
            team, dept  = _get_team_dept(e)

            obj, created = Profile.objects.update_or_create(auto_id=e.emp_id, 
                defaults = {'name':e.emp_name, 'email':e.email, 'team':team, 'dept':dept, 'manager': mgr, 'department': e.dept_name, 'job': e.job, 'usertype': 'EMP', 'notes': '<auto-updated>' })
            obj.CBU.set( CBU.objects.filter(name__exact=settings.MY_CBU))   # many-to-many, 

            # FIXME, Django user SQL...
            # if hasattr(obj, 'user') and obj.user:
            #     User.objects.filter(user=obj.user).update(is_active=True, is_staff=True)

            #     if not obj.user.groups.filter(name=settings.DEFAULT_AUTH_GROUP).exists():    
            #         try:
            #             user_group = Group.objects.get(name=settings.DEFAULT_AUTH_GROUP)
            #             if user_group: 
            #                 obj.user.groups.add(user_group) 
            #         except:
            #             pass

def _get_mgr(id):
    try: 
        mgr = Profile.objects.get(auto_id__exact=id).name
    except:
        mgr = None       
    return mgr

"""
    search org hierarchy for team, dept, and div 
"""
def _get_team_dept(e):
    if   e.l == 1:
        team, dept = None, None 
    elif e.l == 2:
        team = None
        dept = Dept.objects.get(name__exact=e.dept_name) 

    else:
        # team level
        try: 
            team = Team.objects.get(name__exact=e.dept_name) 

            mgr = Employee.objects.get(emp_id__exact=e.manager_id)
            while mgr.l == 3:
                mgr = Employee.objects.get(emp_id__exact=mgr.manager_id)
            dept = Dept.objects.get(name__exact=mgr.dept_name)
        except:
            mgr, team, dept = None, None, None

        # update team head, team's dept
        if team and not team.head:
            Team.objects.filter(id=team.id).update(head = Profile.objects.get(auto_id__exact=e.manager_id))
        if team and not team.dept:
            Team.objects.filter(id=team.id).update(dept=dept)


        # if div level (special case)
        if mgr and mgr.l in (1, 2):  # no dept exist, then just use it
            pass
        else:
            # find dept level manager
            mgr = Employee.objects.get(emp_id__exact=mgr.manager_id)
            while mgr.l == 2:
                mgr = Employee.objects.get(emp_id__exact=mgr.manager_id)

        # updatedept head
        if dept and not dept.head:
            Dept.objects.filter(id=dept.id).update(head=Profile.objects.get(auto_id__exact=mgr.emp_id))

        # get next level - div, if level 1, then just use it
        if mgr and mgr.l == 1:
            pass
        else:
            mgr = Employee.objects.get(emp_id__exact=mgr.manager_id)
        
        try:
            div = Div.objects.get(name__exact=mgr.dept_name)
        except:
            div = None            

        # update dept's div
        if dept and not dept.div:
            Dept.objects.filter(id=dept.id).update(div=div)

        # update div head
        if div and not div.head:
            try:
                Div.objects.filter(id=div.id).update(head=Profile.objects.get(auto_id__exact=mgr.emp_id))
            except:
                pass

    # return final result
    return team, dept


"""
    update employee data
"""
def _update_emp():
    if not settings.SAP:
        logger.warning('SAP connection is not enabled in setting')
        return

    timezone = pytz.timezone(settings.TIME_ZONE)

    results = get_sap_emp_data()
    # table = 'ZSUSRMT0010'
    # fields = ['USER_ID', 'CREATE_DATE', 'TERMINATE_DATE', 'USER_NAME', 'EMAIL', 'COSTCENTER', 'DEPT_CODE', 'DEPT_NAME', 'CHARGE_JOB', 'POS_LEVEL', 'SUPERVISORID', 'DUTY_CODE' ]
    # where  = []    # "USER_ID = 'xxx'"    # "TERMINATE_DATE = '00000000'" ] -> terminated -> delete from current emp table  
    # maxrows = 10000
    # # starting row to return
    # fromrow = 0

    # with Connection(**settings.SAP_CONN) as conn:
    #     # query SAP
    #     results, headers = sap_qry(conn, table, fields, where, maxrows, fromrow)

    # # get latest per emp_id, create_date, sort first / better to select latest... 
    # sorted_results = sorted( results, key=lambda x:( x[0], x[1] ) )

    # # remove all left/right spaces
    # for r in sorted_results:
    #     r[:] = [info.strip() for info in r]

    new_emp, upd_emp = [], []
    for item in results:
        if item[1][:1] == '0' or item[9] == '' or item[5] == '':  # invalid record, skip
            continue

        if item[11] in ('1000', '2000', '0600', '0100'):    #Sub-div/division/president
            level = 1
        elif item[11] == '3000':            #Dept
            level = 2
        elif item[11] in ('4000', '5000'):  #Section and members
            level = 3
        else:
            level = 3
        
        # ctime = datetime(1, 1, 1, 0, 0)   # initial date/time
        cdate = timezone.localize(datetime.strptime(item[1], '%Y%m%d'))
        tdate = timezone.localize(datetime.strptime(item[2], '%Y%m%d')) if item[2][:1] != '0' else None
        email = item[4].lower()     #.split('@')[0].lower() 


        obj, created = Employee.objects.update_or_create(emp_id=item[0], defaults = { 'create_date':cdate, 'terminated':tdate, 'emp_name':item[3], 'email':email, 
                                'cc':item[5], 'dept_code':item[6], 'dept_name':item[7], 'job':item[8], 'l':level, 'manager_id':item[10] })

        # if int( Employee.objects.filter(emp_id=item[0]).count() ) > 0:
        #         Employee.objects.filter(emp_id=item[0]).update(emp_id=item[0], create_date=cdate, terminated=tdate, emp_name=item[3], email=email, cc=item[5], dept_code=item[6], dept_name=item[7], job=item[8], l=level, manager_id=item[10])
        # else:
        #     Employee.objects.create(emp_id=item[0], create_date=cdate, terminated=tdate, emp_name=item[3], email=email, cc=item[5], dept_code=item[6], dept_name=item[7], job=item[8], l=level, manager_id=item[10])

        if created:
            new_emp.append(obj.id)
        else:
            upd_emp.append(obj.id)

    del_emp = Employee.objects.exclude(id__in=new_emp).exclude(id__in=upd_emp)
    del_emp.delete()


"""
    crontab scheduling
"""
def _update_emp_org_profile():
    # interface from SAP
    _update_emp()
    # create/update div, dept, team from current emp data
    _update_org()
    # create/update profile and assign div, dept, team
    # update head for div,dept,team 
    _update_profile()

"""
    WBS updating: crontab scheduling
"""
def _update_wbs():
    ret = {"E_RET": "E", "E_MSG": ""}
    timezone = pytz.timezone("America/Los_Angeles")

    if not settings.SAP:
        ret["E_MSG"] = "SAP connection is not enabled in setting"
        return ret
        
    data = {}
    # sap_connection = settings.SAP_CONFIG['servers']['IDE']
    # with Connection(**sap_connection) as conn:
    with Connection(**settings.SAP_CONN) as conn:
        try:
            result = conn.call('ZPS_PROJECT_LIST', ET_TAB=[])
            for item in result['ET_TAB']:
                if item['ZZLARGE'] == 'S':
                    tObj = {}
                    tObj['PSPID'] = item['PSPID']
                    tObj['POST1'] = item['POST1']
                    tObj['SORTL'] = item['SORTL']
                    tObj['ERNAM'] = item['ERNAM_PRPS']
                    tObj['ERDAT'] = item['ERDAT_PRPS']
                    tObj['AEDAT'] = item['AEDAT_PRPS']
                    tObj['STATUS'] = item['STATUS']
                    tObj['BUDGET'] = item['BUDGET']
                    data[ tObj['PSPID'] ] = tObj
        except Exception as e:
            ret["E_MSG"] = 'RFC Error: ' + str(e)
            return ret

    try:
        for key in data.keys():
            item = data[key]
            user = None
            userSet = User.objects.filter(username=item['ERNAM'].lower())
            if len(userSet) > 0:
                user = userSet[0]
            ctime = None
            if item['ERDAT'] != '':
                ctime = datetime.strptime(item['ERDAT'], '%Y%m%d') #.strftime('%Y-%m-%d')
                ctime = timezone.localize(ctime)
            utime = None
            if item['AEDAT'] != '':
                utime = datetime.strptime(item['AEDAT'], '%Y%m%d') #.strftime('%Y-%m-%d')
                utime = timezone.localize(utime)
            wbsSet = WBS.objects.filter(wbs=item['PSPID'])
            if (len(wbsSet) > 0):
                if ctime == None:
                    ctime = wbsSet[0].created_at
                if utime == None:
                    utime = wbsSet[0].updated_on
                wbsSet.update(name = item['POST1'], cbu = item['SORTL'], status = item['STATUS'], budget = item['BUDGET'], created_by = user, created_at = ctime, updated_on = utime)
            else:
                wbs = WBS(wbs = item['PSPID'], name = item['POST1'], cbu = item['SORTL'], status = item['STATUS'], budget = item['BUDGET'], created_by = user, created_at = ctime, updated_on = utime)
                wbs.save()
    except Exception as e:
        ret["E_MSG"] = 'An error occurs during DB operations' + str(e)
        return ret
    ret["E_RET"] = 'S'
    return ret


    # def import_func_deprecated(modeladmin, request, queryset):
        
    #     data = {}
    #     with Connection(**settings.SAP_CONN) as conn:
    #         try:
    #             # abap_structure = {'RFCINT4': 345}
    #             # abap_table = [abap_structure]
    #             # result = conn.call('STFC_STRUCTURE', IMPORTSTRUCT=abap_structure, RFCTABLE=abap_table)
    #             # print (result)

    #             ROWS_AT_A_TIME = 200

    #             table = 'ZSUSPSV0020'
    #             fields = [ 'PSPID', 'POST1', 'SORTL', 'ERNAM_PRPS', 'ERDAT_PRPS', 'AEDAT_PRPS' ]
    #             options = [{ 'TEXT': "PSPID like 'S%'" }]

    #             rowskips = 0
    #             while True:
    #                 result = conn.call('RFC_READ_TABLE'
    #                                 , QUERY_TABLE=table
    #                                 , OPTIONS = options
    #                                 , FIELDS = fields
    #                                 , ROWSKIPS = rowskips, ROWCOUNT = ROWS_AT_A_TIME)
    #                 rowskips += ROWS_AT_A_TIME
    #                 for item in result['DATA']:
    #                     tObj = { 'STATUS': '0' }
    #                     for idx, field in enumerate(result['FIELDS']):
    #                         start = int(field['OFFSET'])
    #                         end = start + int(field['LENGTH'])
    #                         tObj[field['FIELDNAME']] = item['WA'][start:end].strip()
    #                     data[tObj['PSPID']] = tObj

    #                 if len(result['DATA']) < ROWS_AT_A_TIME:
    #                     break        

    #             table = 'ZSUSPST1000'
    #             fields = [ 'PSPID', 'STATUS' ]
    #             options = [{ 'TEXT': "PSPID like 'S%' and VERSN eq '0'" }]

    #             rowskips = 0
    #             while True:
    #                 result = conn.call('RFC_READ_TABLE'
    #                                 , QUERY_TABLE=table
    #                                 , OPTIONS = options
    #                                 , FIELDS = fields
    #                                 , ROWSKIPS = rowskips, ROWCOUNT = ROWS_AT_A_TIME)
    #                 rowskips += ROWS_AT_A_TIME
    #                 for item in result['DATA']:
    #                     tObj = {}
    #                     for idx, field in enumerate(result['FIELDS']):
    #                         start = int(field['OFFSET'])
    #                         end = start + int(field['LENGTH'])
    #                         tObj[field['FIELDNAME']] = item['WA'][start:end].strip()
    #                     if tObj['PSPID'] in data:
    #                         data[ tObj['PSPID'] ][ 'STATUS' ] = tObj[ 'STATUS' ]

    #                 if len(result['DATA']) < ROWS_AT_A_TIME:
    #                     break

    #         except Exception as e:
    #             print ('RFC error' + str(e))
    #             return

    #         try:
    #             for key in data.keys():
    #                 item = data[key]
    #                 # print(item)
    #                 # item = data['S21-0034']
    #                 # item['ERNAM_PRPS']
    #                 user = None
    #                 userSet = User.objects.filter(username=item['ERNAM_PRPS'].lower())
    #                 if len(userSet) > 0:
    #                     user = userSet[0]
    #                 ctime = None
    #                 if item['ERDAT_PRPS'] != '00000000':
    #                     ctime = datetime.strptime(item['ERDAT_PRPS'], '%Y%m%d') #.strftime('%Y-%m-%d')
    #                 utime = None
    #                 if item['AEDAT_PRPS'] != '00000000':
    #                     utime = datetime.strptime(item['AEDAT_PRPS'], '%Y%m%d') #.strftime('%Y-%m-%d')
    #                 wbsSet = WBS.objects.filter(wbs=item['PSPID'])
    #                 if (len(wbsSet) > 0):
    #                     if ctime == None:
    #                         ctime = wbsSet[0].created_at
    #                     if utime == None:
    #                         utime = wbsSet[0].updated_on
    #                     wbsSet.update(name = item['POST1'], cbu = item['SORTL'], status = item['STATUS'], created_by = user, created_at = ctime, updated_on = utime)
    #                 else:
    #                     wbs = WBS(wbs = item['PSPID'], name = item['POST1'], cbu = item['SORTL'], status = item['STATUS'], created_by = user, created_at = ctime, updated_on = utime)
    #                     wbs.save()
    #         except Exception as e:
    #             print ('DB error' + str(e))
    #             return

    #         # print(data)
    #         # pass

    # #     try:

    # #     config = ConfigParser()
    # #     config.read('sapnwrfc.cfg')
    # #     params_connection = config._sections['connection']
    # #     conn = Connection(**params_connection)

    # #     options = [{ 'TEXT': "PSPID like 'S%'"}]
    # #     fields = ['PSPID','POST1','STSPD']
    # #     pp = PrettyPrinter(indent=4)
    # #     ROWS_AT_A_TIME = 10 
    # #     rowskips = 0
    #         # while True:
    #         #     print u"----Begin of Batch---"
    #         #     result = conn.call('RFC_READ_TABLE', \
    #         #                         QUERY_TABLE = 'ZSUSPSV0020', \
    #         #                         OPTIONS = options, \
    #         #                         FIELDS = fields, \
    #         #                         ROWSKIPS = rowskips, ROWCOUNT = ROWS_AT_A_TIME)
    #         #     pp.pprint(result['DATA'])
    #         #     rowskips += ROWS_AT_A_TIME
    #         #     if len(result['DATA']) < ROWS_AT_A_TIME:
    #         #         break
    #     # except CommunicationError:
    #     #     print u"Could not connect to server."
    #     #     raise
    #     # except LogonError:
    #     #     print u"Could not log in. Wrong credentials?"
    #     #     raise
    #     # except (ABAPApplicationError, ABAPRuntimeError):
    #     #     print u"An error occurred."
    #     #     raise

    #     pass    #queryset.update(status='p')

