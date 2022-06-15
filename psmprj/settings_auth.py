# Auth related settings

from . import env
import ldap
from django_auth_ldap.config import LDAPSearch


AUTH_LDAP_SERVER_URI = env('AUTH_LDAP_SERVER_URI', "ldap://ldap.example.com")
AUTH_LDAP_BIND_DN = env('AUTH_LDAP_BIND_DN', "cn=admin,dc=example,dc=com")
AUTH_LDAP_BIND_PASSWORD = env('AUTH_LDAP_BIND_PASSWORD', "test@1234")

AUTH_LDAP_STRING = env('AUTH_LDAP_STRING', "OU=,DC=,DC=" )

AUTH_LDAP_USER_SEARCH = LDAPSearch(
    AUTH_LDAP_STRING, 
    ldap.SCOPE_SUBTREE, 
    "sAMAccountName=%(user)s"
    )
AUTH_LDAP_USER_ATTR_MAP = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# https://stackoverflow.com/questions/43980247/django-auth-ldap-default-values-for-newly-created-user
#FIXME TODO
# AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()
# AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
#     AUTH_LDAP_STRING,
#     ldap.SCOPE_SUBTREE,
#     '(objectClass=group)'
# )
# AUTH_LDAP_GROUP_STAFF = env('AUTH_LDAP_GROUP_STAFF', "cn=groupname,OU=Groups,OU=example,DCcom")

# from django_auth_ldap.config import ActiveDirectoryGroupType
# AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
#             "dc=hke,dc=local", ldap.SCOPE_SUBTREE, "(objectCategory=Group)"
#             )
# AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType(name_attr="cn")
# AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#     "is_staff": AUTH_LDAP_GROUP_STAFF
#     # "is_staff": "cn=staff,ou=django,ou=groups,dc=example,dc=com",
# }


AUTH_LDAP_FIND_GROUP_PERMS = False
AUTH_LDAP_CACHE_GROUPS = False
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 1  # 1 hour cache


# from decouple import config
# # values you got from step 2 from your Mirosoft app
# MICROSOFT_AUTH_CLIENT_ID = config("MICROSOFT_AUTH_CLIENT_ID")
# MICROSOFT_AUTH_CLIENT_SECRET = config("MICROSOFT_AUTH_CLIENT_SECRET")
# # Tenant ID is also needed for single tenant applications
# MICROSOFT_AUTH_TENANT_ID = config("MICROSOFT_AUTH_TENANT_ID")
# MICROSOFT_AUTH_LOGIN_TYPE = 'ma'

# client_id = config("MICROSOFT_AUTH_CLIENT_ID")
# client_secret = config("MICROSOFT_AUTH_CLIENT_SECRET")
# tenant_id = config("MICROSOFT_AUTH_TENANT_ID")
# AUTH_ADFS = {
#     'AUDIENCE': client_id,
#     'CLIENT_ID': client_id,
#     'CLIENT_SECRET': client_secret,
#     'CLAIM_MAPPING': {'first_name': 'given_name',
#                       'last_name': 'family_name',
#                       'email': 'upn'},
#     'GROUPS_CLAIM': 'roles',
#     'MIRROR_GROUPS': True,
#     'USERNAME_CLAIM': 'upn',
#     'TENANT_ID': tenant_id,
#     'RELYING_PARTY_ID': client_id,
# }
