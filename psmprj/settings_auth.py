# Auth related settings

from . import env


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
