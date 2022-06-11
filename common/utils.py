import enum
from django.utils.translation import gettext_lazy as _

ROLES = (
    ("ADMIN", "ADMIN"),
    ("STAFF", "STAFF"),
    ("USER", "USER"),
)

class Decision(enum.Enum):
    NEW = '00-New'
    ASSIGNED = '10-Assigned'
    PENDING  = '20-Pending'
    REVIEW   = '30-Reviewing'
    ACCEPTED = '50-Accepted'
    REJECTED = '60-Rejected'
    DUPL     = '70-Duplicate'
DECISIONS = (
    (Decision.NEW.value,      _('New')),
    (Decision.ASSIGNED.value, _('Assigned')),
    (Decision.PENDING.value,  _('Pending')),
    (Decision.REVIEW.value,   _('Reviewing')),
    (Decision.ACCEPTED.value, _('Accepted')),
    (Decision.REJECTED.value, _('Rejected')),
    (Decision.DUPL.value,     _('Duplicate'))
)
# this way is possible... no translation
            # (ReviewTypes.PRO.value, 'ReviewType - ' + ReviewTypes.PRO.value[3:]),
            # (ReviewTypes.SEC.value, 'ReviewType - ' + ReviewTypes.SEC.value[3:]),

class State(enum.Enum):
    """
    Status of completion of the Project
    (codes are prefixed with numbers to be easily sorted in the DB).
    """
    BACKLOG = '00-backlog'
    TO_DO   = '10-to-do'
    DOING   = '20-doing'
    HOLD    = '30-on_hold'
    DONE    = '40-done'
    CANCEL  = '50-cancel'
# from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
STATES = (
    (State.BACKLOG.value, _('Backlog')),
    (State.TO_DO.value, _('To_Do')),
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
    LOW = '00-Low'
    NORMAL = '10-Normal'
    HIGH = '20-High'
    CRITICAL = '30-Critical'    #urgent

PRIORITIES = (
    (Priority.LOW.value, _('Low')),
    (Priority.NORMAL.value, _('Normal')),
    (Priority.HIGH.value, _('High')),
    (Priority.CRITICAL.value, _('Critical')),   
)


class Status(enum.Enum):
    NA = '00-N/A'
    GREEN = '10-Green'
    YELLOW = '20-Yellow'
    RED = '30-Red'
    COMPLETED = '90-Completed'

STATUS = (
    (Status.GREEN.value, _('Green')),
    (Status.YELLOW.value, _('Yellow')),
    (Status.RED.value, _('Red')),
    (Status.COMPLETED.value, _('Completed')),
    (Status.NA.value, _('N/A')),
)

class Phase(enum.Enum):
    IDEATION =  '00-Ideation'
    PRE_PLAN =  '10-Pre-Planning'
    PLANNING =  '20-Planning'
    DESIGN =    '30-Design'
    DEVELOP =   '40-Develop'
    TESTING =   '50-Testing'
    LAUNCH =    '60-Launch'
    COMPLETED = '70-Completed'
    CLOSED =    '80-Closed'

PHASE = (
    (Phase.IDEATION.value, _('Ideation')),
    (Phase.PRE_PLAN.value, _('Pre-Planning')),
    (Phase.PLANNING.value, _('Planning')),
    (Phase.DESIGN.value, _('Design')),
    (Phase.DEVELOP.value, _('Development')),
    (Phase.TESTING, _('Testing')),
    (Phase.LAUNCH.value, _('Launch')),        
    (Phase.COMPLETED.value, _('Completed')),        
    (Phase.CLOSED.value, _('Closed')),
)

class PrjType(enum.Enum):
    MAJOR = '10-Major'
    SMALL = '20-Small'
    ENH   = '30-Enhancement'
    UNC   = '00-Unclassifed'

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
    (ReviewTypes.APP.value, _('40-App_Architect')),
    (ReviewTypes.MGT.value, _('90-Management'))
)

class Versions(enum.Enum):
    V00 = '00'
    V10 = '10'
    V11 = '11'
    V12 = '12'
    V20 = '20-Final'
VERSIONS = (
    (Versions.V10.value, _('10')),
    (Versions.V11.value, _('11')),
    (Versions.V12.value, _('12')),
    (Versions.V20.value, _('Final version')),
)

PUBLISH = (
	(0, "Draft"),
	(1, "Publish"),
	(2, "Delete")
)
