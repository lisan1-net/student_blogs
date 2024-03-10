from django import template
from django.template.defaultfilters import mark_safe
from django.core.paginator import Paginator

register = template.Library()


@register.filter
def url_with_page(request, page):
    params = request.GET.copy()
    params['page'] = page
    return request.path + '?' + params.urlencode()


@register.simple_tag
def highlight_range(text, start, end, surrounding_words=5):
    text_before = text[:start]
    highlighted_text = text[start:end]
    text_after = text[end:]
    words_before = text_before.split()
    words_after = text_after.split()
    prefix = Paginator.ELLIPSIS if len(words_before) > surrounding_words else ''
    suffix = Paginator.ELLIPSIS if len(words_after) > surrounding_words else ''
    return mark_safe(
        prefix + " ".join(words_before[-surrounding_words:]) +
        f' <mark class="p-0 bg-warning">{highlighted_text}</mark> ' + " ".join(words_after[:surrounding_words])
        + suffix
    )
