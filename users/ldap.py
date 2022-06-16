# https://dev.to/lquenti/dynamic-group-based-ldap-authentication-with-django-and-regex-1h4p
import re
import ldap

from django_auth_ldap.backend import LDAPBackend, _LDAPUser
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.conf import settings


class GroupLDAPBackend(LDAPBackend):
    default_settings = {
        # Our new settings
        # Lets call the RegEx GROUP_REGEX for simplicity
        # "GROUP_REGEX": re.compile(r"^*HISNA$"),
        "GROUP_SEARCH": LDAPSearch(
            settings.AUTH_LDAP_GROUP_STR,
            ldap.SCOPE_SUBTREE,     #"(objectClass=top)"
            "(objectClass=group)"
        ),
        "GROUP_TYPE": GroupOfNamesType(),

        # # Define a group required to login.
        # "AUTH_LDAP_REQUIRE_GROUP" : "CN=..._USERS,DC=example,DC=com"
        # 
        "AUTH_LDAP_USER_FLAGS_BY_GROUP" : {
            "is_staff": settings.AUTH_LDAP_GROUP_STAFF,      
        },
        # For more granular permissions, we can map LDAP groups to Django groups.
        "AUTH_LDAP_FIND_GROUP_PERMS" : True,
        # Cache groups for one hour to reduce LDAP traffic
        "AUTH_LDAP_CACHE_GROUPS" : True,
        "AUTH_LDAP_GROUP_CACHE_TIMEOUT" : 3600,

        # All those settings are overwriting base class values
        "SERVER_URI": settings.AUTH_LDAP_SERVER_URI,
        "CACHE_TIMEOUT": 3600,

        # Those settings should probably be overwritten by the settings.py
        "BIND_DN": settings.AUTH_LDAP_BIND_DN,
        "BIND_PASSWORD": settings.AUTH_LDAP_BIND_PASSWORD,
        "USER_SEARCH": LDAPSearch(
            settings.AUTH_LDAP_STRING,
            # If you know, that all your users logging in are on that 
            # exact ou depth specified above, you can get better performance
            # by using ldap.SCOPE_BASE or for that depth and its direct 
            # children ldap.SCOPE_ONELEVEL, see python-ldap documentation for
            # more.
            ldap.SCOPE_SUBTREE,
            "sAMAccountName=%(user)s"   #"(uid=%(user)s)"
        ),
        "AUTH_LDAP_USER_ATTR_MAP" : {
            "username"  : "sAMAccountName",
            "first_name": "givenName",
            "last_name" : "sn",
            "email"     : "mail",
            # "manager"   : "manager",
            # "job"       : "job",
            # "department": "department",
            # "mobile"    : "mobile",
        },

    }    

    def authenticate_ldap_user(self, ldap_user: _LDAPUser, password: str):
        # This is the default implemented authentication
        # user = User.objects.create_user('username', None, None)
        user = ldap_user.authenticate(password)

        # If the authentication was denied, we have to return None
        if not user:
            return None

        #FIXME -empty group....
        ldap_groups = ldap_user.group_names
        # ldap_groups = {x for x in ldap_groups if self.settings.GROUP_REGEX.match(x)}

        if len(ldap_groups) == 0:
            return user

        self.create_groups_and_assign_user_to_it(user, ldap_groups)
        return user

    def create_groups_and_assign_user_to_it(self, user, ldap_groups):
        for group_name in ldap_groups:
            django_group, was_created = Group.objects.get_or_create(name=group_name)
            django_group.user_set.add(user)

if settings.DEBUG:
    pass
    # import logging
    # logger = logging.getLogger('django_auth_ldap')
    # logger.addHandler(logging.StreamHandler())
    # logger.setLevel(logging.DEBUG)


    # default_settings = {
    #     # All those settings are overwriting base class values
    #     "SERVER_URI": "ldaps://url.to.our.dc.domain.com",
    #     "CACHE_TIMEOUT": 3600,

    #     # Those settings should probably be overwritten by the settings.py
    #     "BIND_DN": "",
    #     "BIND_PASSWORD": "",
    #     "USER_SEARCH": LDAPSearch(
    #     "OU=<OU_OF_USER_LOGGING_IN>, OU=..., DC=..., DC=domain, DC=com",
    #     # If you know, that all your users logging in are on that 
    #     # exact ou depth specified above, you can get better performance
    #     # by using ldap.SCOPE_BASE or for that depth and its direct 
    #     # children ldap.SCOPE_ONELEVEL, see python-ldap documentation for
    #     # more.
    #     ldap.SCOPE_SUBTREE,
    #     "(uid=%(user)s)"
    #     ),
            
    # }