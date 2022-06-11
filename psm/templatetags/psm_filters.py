from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
# from numerize import numerize
# a = numerize.numerize(1234567.12, 2)
# 1000 -> 1k
# 1500 -> 1.5k
# 1000000 -> 1M

register = template.Library()

@register.filter
def currency(dollars, arg):
    if arg == "m":
        dollars = round(float(dollars/1000000), 2)
        return "$%s%sM" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
    elif arg == "k":
        dollars = round(float(dollars/1000), 0)
        return "$%s k" % intcomma(int(dollars))
    else:
        dollars = round(float(dollars), 2)
        return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])

