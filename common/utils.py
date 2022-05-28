import enum
from django.utils.translation import gettext_lazy as _

ROLES = (
    ("ADMIN", "ADMIN"),
    ("USER", "USER"),
)

class Decision(enum.Enum):
    NEW = 'New'
    ASSIGNED = 'Assigned'
    PENDING  = 'Pending'
    REVIEWED = 'Reviewed'
    CLOSED   = 'Closed'
    REJECTED = 'Rejected'
    DUPL     = 'Duplicate'
DECISIONS = (
    (Decision.NEW.value,      _('New')),
    (Decision.ASSIGNED.value, _('Assigned')),
    (Decision.PENDING.value,  _('Pending')),
    (Decision.REVIEWED.value, _('Reviewed')),
    (Decision.CLOSED.value,   _('Closed')),
    (Decision.REJECTED.value, _('Rejected')),
    (Decision.DUPL.value,     _('Duplicate'))
)

class State(enum.Enum):
    """
    Status of completion of the Project
    (codes are prefixed with numbers to be easily sorted in the DB).
    """
    BACKLOG = '00-backlog'
    TO_DO = '10-to-do'
    DOING = '20-doing'
    HOLD = '30-on-hold'
    DONE = '50-done'
    CANCEL = '90-cancel'
# from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
STATES = (
    (State.BACKLOG.value, _('Backlog')),
    (State.TO_DO.value, _('To Do')),
    (State.DOING.value, _('Doing')),
    (State.HOLD.value, _('Blocked')),
    (State.DONE.value, _('Done')),
    (State.CANCEL.value, _('Canceled'))
)

class Priority(enum.Enum):
    """
    The priority of the Project
    (codes are prefixed with numbers to be easily sorted in the DB).
    """
    LOW = '00-low'
    NORMAL = '10-normal'
    HIGH = '20-high'
    CRITICAL = '30-critical'    #urgent

PRIORITIES = (
    (Priority.LOW.value, _('Low')),
    (Priority.NORMAL.value, _('Normal')),
    (Priority.HIGH.value, _('High')),
    (Priority.CRITICAL.value, _('Critical')),   
)


class Status(enum.Enum):
    NA = '00-notApplicable'
    GREEN = '10-green'
    YELLOW = '20-yellow'
    RED = '30-red'
    COMPLETED = '90-completed'

STATUS = (
    (Status.GREEN.value, _('Green')),
    (Status.YELLOW.value, _('Yellow')),
    (Status.RED.value, _('Red')),
    (Status.COMPLETED.value, _('Completed')),
    (Status.NA.value, _('N/A')),
)

class Phase(enum.Enum):
    PRE_PLAN = '00-Pre-Planning'
    PLANNING = '10-Planning'
    DESIGN =   '20-Design'
    DEVELOP =  '30-Develop'
    TESTING =  '40-Testing'
    LAUNCH =   '50-Launch'
    COMPLETED = '80-Completed'
    CLOSED =   '90-Closed'

PHASE = (
    ('00-Pre-Planning',"Pre-Planning"),
    ('10-Planning',"Planning"),
    ('20-Planning',"Design"),
    ('30-Planning',"Development"),
    ('40-Testing',"Testing"),        
    ('50-Launch',"Launch"),        
    ('60-Completed',"Completed"),        
    ('90-Closed',"Closed")        
)

class PrjType(enum.Enum):
    MAJOR = '00-Major'
    SMALL = '10-Small'
    ENH   = '20-Enhancement'
    UNC   = '90-Unclassifed'

PRJTYPE = (
    (PrjType.MAJOR.value, _('Major')),
    (PrjType.SMALL.value, _('Small')),
    (PrjType.ENH.value, _('Enhancement')),
    (PrjType.UNC.value, _('Unclassified')),
)

class State3(enum.Enum):
    TBD = '0-TBD'
    YES = '1-Yes'
    NO  = '2-No'
STATE3 = (
    (State3.TBD.value, _('TBD')),
    (State3.YES.value, _('Yes')),
    (State3.NO.value, _('No')),
)

class ReviewTypes(enum.Enum):
    PRO = '10-Procurement'
    SEC = '20-Security'
    INF = '30-Infra-Architecture'
    APP = '40-App-Architecture'
    MGT = '90-Management'
REVIEWTYPES = (
    (ReviewTypes.PRO.value, _('10-Procurement')),
    (ReviewTypes.SEC.value, _('20-Security')),
    (ReviewTypes.INF.value, _('30-Infrastructure')),
    (ReviewTypes.APP.value, _('40-App_Archit')),
    (ReviewTypes.MGT.value, _('90-Management'))
)

PUBLISH = (
	(0, "Draft"),
	(1, "Publish"),
	(2, "Delete")
)
