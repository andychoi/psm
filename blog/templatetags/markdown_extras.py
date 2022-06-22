# blog/templatetags/markdown_extras.py
from django import template
from django.template.defaultfilters import stringfilter

# markdown -> markdown2
# import markdown as md
import markdown2 

register = template.Library()

# @register.filter()
# @stringfilter
# def markdown(content):
#     return md.markdown(content, extensions=['markdown.extensions.fenced_code'])

# {{ var|md2:"bar" }}
@register.filter()
@stringfilter
def md2(content, tag='psm-md2'):
    # tag2 = tag if tag else 'psm-md2'
    return f"<div class='{tag}'>" + markdown2.markdown(content, extras=["cuddled-lists", "break-on-newline", "tables"]) + "</div><!--md2-->" 


