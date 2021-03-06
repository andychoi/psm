import enum
from django.utils.translation import gettext_lazy as _



class Action(enum.Enum):
    NEW = '00-New'
    ASSIGNED = '10-Assigned'
    PENDING  = '20-Pending'
    REVIEW   = '30-Reviewing'
    ACCEPTED = '50-Accepted'
    COMPLETED= '60-Completed'
    REJECTED = '70-Rejected'
    DUPL     = '80-Duplicate'
ACTIONS = (
    (Action.NEW.value,       _('New')),
    (Action.ASSIGNED.value,  _('Assigned')),
    (Action.PENDING.value,   _('Pending')),
    (Action.REVIEW.value,    _('Reviewing')),
    (Action.ACCEPTED.value,  _('Accepted')),
    (Action.COMPLETED.value, _('Completed')),
    (Action.REJECTED.value,  _('Rejected')),
    (Action.DUPL.value,      _('Duplicate'))
)
# this way is possible... no translation
            # (ReqTypes.PRO.value, 'ReqType - ' + ReqTypes.PRO.value[3:]),
            # (ReqTypes.SEC.value, 'ReqType - ' + ReqTypes.SEC.value[3:]),

class State(enum.Enum):
    """
    Status of completion of the Project
    (codes are prefixed with numbers to be easily sorted in the DB).
    """
    BACKLOG = '00-backlog'
    TODO    = '10-todo'
    DOING   = '20-doing'
    HOLD    = '30-hold'
    DONE    = '40-done'
    CANCEL  = '80-cancel'
    DELETE  = '90-delete'
# from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
STATES = (
    (State.BACKLOG.value, _('Backlog')),
    (State.TODO.value, _('To_Do')),
    (State.DOING.value, _('Doing')),
    (State.HOLD.value, _('Blocked')),
    (State.DONE.value, _('Done')),
    (State.CANCEL.value, _('Canceled')),
    (State.DELETE.value, _('Deleted')),
)
STATE_VALID  = { State.BACKLOG.value, State.TODO.value, State.DOING.value, State.HOLD.value, State.DONE.value }
STATE_OPEN = { State.BACKLOG.value, State.TODO.value, State.DOING.value, State.HOLD.value,  }
STATE_WORK = { State.TODO.value, State.DOING.value,  }

class State2(enum.Enum):
    OPEN    = '00-Open'
    CLOSE   = '10-Close'
    CANCEL  = '80-cancel'
# from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
STATE2 = (
    (State2.OPEN.value, _('Open')),
    (State2.CLOSE.value, _('Close')),
    (State2.CANCEL.value, _('Cancel')),
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
    NA =        '00-N/A'
    GREEN =     '10-Green'
    YELLOW =    '20-Yellow'
    RED =       '30-Red'
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
    PRE_PLAN =  '10-Pre_Planning'
    PLANNING =  '20-Planning'
    DESIGN =    '30-Design'
    DEVELOP =   '40-Develop'
    TESTING =   '50-Testing'
    LAUNCH =    '60-Launch'
    COMPLETED = '70-Completed'
    CLOSED =    '80-Closed'
PHASE = (
    (Phase.IDEATION.value, _('Ideation')),
    (Phase.PRE_PLAN.value, _('Pre_Planning')),
    (Phase.PLANNING.value, _('Planning')),
    (Phase.DESIGN.value, _('Design')),
    (Phase.DEVELOP.value, _('Development')),
    (Phase.TESTING.value, _('Testing')),
    (Phase.LAUNCH.value, _('Launch')),        
    (Phase.COMPLETED.value, _('Completed')),        
    (Phase.CLOSED.value, _('Closed')),
)
PHASE_BACKLOG = (
    Phase.IDEATION.value, Phase.PRE_PLAN.value )
PHASE_WORK = (
    Phase.PLANNING.value, Phase.DESIGN.value, 
    Phase.DEVELOP.value, Phase.TESTING.value, Phase.LAUNCH.value )
PHASE_OPEN = (
    Phase.IDEATION.value, Phase.PRE_PLAN.value, Phase.PLANNING.value, Phase.DESIGN.value, 
    Phase.DEVELOP.value, Phase.TESTING.value, Phase.LAUNCH.value )
PHASE_CLOSE = (
    Phase.COMPLETED.value, Phase.CLOSED.value )

class PrjType(enum.Enum):
    INF  = '10-Infrastructure'
    APP  = '20-Application'
    ASS  = '30-Assessment/Audit'
    ENH  = '40-Big_Enhancement'
    UNC  = '00-Unclassifed'

PRJTYPE = (
    (PrjType.INF.value, _('Infrastructure')),
    (PrjType.APP.value, _('Application')),
    (PrjType.ASS.value, _('Assessment/Audit')),
    (PrjType.ENH.value, _('Big_Enhancement')),
    # (PrjType.UNC.value, _('Unclassified')),
)

class PrjSize(enum.Enum):
    LAR = '10-Large'
    MED = '20-Medium'
    SML = '30-Small'

PRJSIZE = (
    (PrjSize.LAR.value, _('Large')),
    (PrjSize.MED.value, _('Medium')),
    (PrjSize.SML.value, _('Small')),
)

class Action3(enum.Enum):
    TBD = '0-TBD'
    YES = '1-Yes'
    NO  = '2-No'
ACTION3 = (
    (Action3.TBD.value, _('TBD')),
    (Action3.YES.value, _('Yes')),
    (Action3.NO.value, _('No')),
)

class ReqTypes(enum.Enum):
    PRO = '10-Procurement'
    SEC = '20-Security'
    INF = '30-Infra-Architecture'
    APP = '40-App-Architecture'
    MGT = '90-Management'
REQTYPES = (
    (ReqTypes.PRO.value, _('10-Procurement')),
    (ReqTypes.SEC.value, _('20-Security')),
    (ReqTypes.INF.value, _('30-Infrastructure')),
    (ReqTypes.APP.value, _('40-App_Architect')),
    (ReqTypes.MGT.value, _('90-Management'))
)

class Versions(enum.Enum):
    V00 = '00'
    V10 = '10-Initial'
    V11 = '11'
    V12 = '12'
    V20 = '20-BAP (planned)'
    V21 = '21-NEW (Unplanned)'
VERSION_QUEUE = ( Versions.V10.value, Versions.V11.value, Versions.V12.value,  )
VERSION_DONE  = ( Versions.V20.value, Versions.V21.value,   )

VERSIONS = (
    (Versions.V10.value, _('10-Request')),
    (Versions.V11.value, _('11-Review 1')),
    (Versions.V12.value, _('12-Review 2')),
    (Versions.V20.value, _('20-BAP(planned)')),
    (Versions.V21.value, _('21-NEW(unplanned)')),
)

PUBLISH = (
	(0, "Draft"),
	(1, "Publish"),
	(2, "Delete")
)

# https://distantjob.com/blog/junior-front-end-developer-skills/
class SkillLevel(enum.Enum):
    JUNIOR  = '10-Junior'
    MID     = '20-Midlevel'
    SENIOR  = '30-Senior'
    LEAD    = '40-Lead'
SKILLLEVEL = (
    (SkillLevel.JUNIOR.value,   _('Junior')),
    (SkillLevel.MID.value,      _('Midlevel')),
    (SkillLevel.SENIOR.value,   _('Senior')),
    (SkillLevel.LEAD.value,     _('Lead')),
)

# working calendar per region
WCAL = (
	('CA',  "CA"),
	('AL',  "AL"),
	('GA',  "GA"),
	('CA*', "HT"),
)