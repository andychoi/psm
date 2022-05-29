# your_app/templatetags/env_extras.py
# https://stackoverflow.com/questions/62797296/how-to-access-environment-variable-from-html-or-js-in-django
# https://stackoverflow.com/questions/433162/can-i-access-constants-in-settings-py-from-templates-in-django
# always has to restart server when changed...
from django import template
from django.conf import settings

register = template.Library()

# settings value
@register.simple_tag
def get_env_var(name):
    return getattr(settings, name, "")