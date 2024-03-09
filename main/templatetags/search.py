from django import template
from django.template.defaultfilters import mark_safe

register = template.Library()


@register.filter
def url_with_page(request, page):
    params = request.GET.copy()
    params['page'] = page
    return request.path + '?' + params.urlencode()


@register.simple_tag
def highlight_range(text, start, end):
    return mark_safe(
        f'{text[:start]}<mark class="p-0 bg-warning">{text[start:end]}</mark>{text[end:]}'
    )
