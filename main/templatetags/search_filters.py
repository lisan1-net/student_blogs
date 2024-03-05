from re import IGNORECASE, compile, escape as rescape

from django import template
from django.template.defaultfilters import stringfilter, mark_safe

register = template.Library()


@register.filter
@stringfilter
def highlight(value, target):
    rgx = compile(rescape(target), IGNORECASE)
    return mark_safe(rgx.sub(r'<span class="bg-warning">\g<0></span>', value))
