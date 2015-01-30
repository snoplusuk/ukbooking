from django import template
from django.core.urlresolvers import reverse

import calendar
import re

register = template.Library()

@register.filter
def month_name(month_number):
    month_number = int(month_number)
    return calendar.month_name[month_number]

@register.filter
def day_suffix(day):
    day = int(day)
    if day == 0:
        return "0"
    elif 4 <= day <= 20 or 24 <= day <= 30:
        return "%i%s" % (day, "th")
    else:
        return "%i%s" % (day, ["st", "nd", "rd"][day % 10 - 1])
