from django import template
from django.template.defaultfilters import mark_safe
from django.core.paginator import Paginator
from django.urls import reverse

register = template.Library()


@register.filter
def author_icon(author):
    icon_name = ''
    if author.sex == 'M':
        icon_name = 'face'
    elif author.sex == 'F':
        icon_name = 'face_3'
    return mark_safe(f'<span class="material-icons">{icon_name}</span>')


@register.filter
def paragraphs_wrap(content):
    return mark_safe('<p>' + content.replace('\n', '</p><p>') + '</p>')


@register.filter
def url_with_page(request, page):
    params = request.GET.copy()
    params['page'] = page
    return request.path + '?' + params.urlencode()


@register.simple_tag
def highlight_range(text: str, start: int, end: int, pk:int, surrounding_words=5):
    text_before = text[:start]
    highlighted_text = text[start:end]
    text_after = text[end:]
    words_before = text_before.split(' ')
    words_after = text_after.split(' ')
    prefix = Paginator.ELLIPSIS if len(words_before) > surrounding_words else ''
    suffix = Paginator.ELLIPSIS if len(words_after) > surrounding_words else ''
    href = reverse('text', args=[pk])
    onclick = f"window.open('{href}', 'newwindow', 'width=600,height=400'); return false;"
    return mark_safe(
        prefix + " ".join(words_before[-surrounding_words:]) +
        f'<a class="text-warning text-decoration-none" href="{href}" onclick="{onclick}">{highlighted_text}</a>' +
        " ".join(words_after[:surrounding_words]) + suffix
    )
