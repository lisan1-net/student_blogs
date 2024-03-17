from django import template
from django.template.defaultfilters import mark_safe
from django.core.paginator import Paginator
from django.urls import reverse
from django.apps import apps

register = template.Library()


@register.filter
def visible_page_numbers(paginator: Paginator, number: int):
    return paginator.get_elided_page_range(number, on_each_side=2, on_ends=1)


@register.filter
def sex_icon(sex):
    icon_name = ''
    if sex == 'M':
        icon_name = 'face'
    elif sex == 'F':
        icon_name = 'face_3'
    return mark_safe(f'<span class="material-icons">{icon_name}</span>')


@register.filter
def text_type_icon(text_type):
    icon_name = ''
    match text_type:
        case 'SPOKEN':
            icon_name = 'record_voice_over'
        case 'WRITTEN':
            icon_name = 'edit_document'
        case 'NOTEBOOKS':
            icon_name = 'menu_book'
    return mark_safe(f'<span class="material-icons">{icon_name}</span>')


@register.filter
def paragraphs_wrap(content):
    return mark_safe('<p>' + content.replace('\n', '</p><p>') + '</p>')


@register.filter
def url_with_page(request, page):
    params = request.GET.copy()
    params['page'] = page
    return request.path + '?' + params.urlencode()


@register.filter
def search_url_for_word(request, word):
    params = request.GET.copy()
    params['search_query'] = f'"{word}"'
    params.pop('page', None)
    return reverse('home') + '?' + params.urlencode()


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
    onclick = f"window.open('{href}', 'newwindow', 'width=800,height=600'); return false;"
    return mark_safe(
        prefix + " ".join(words_before[-surrounding_words:]) +
        f'<a class="text-warning text-decoration-none" href="{href}" onclick="{onclick}">{highlighted_text}</a>' +
        " ".join(words_after[:surrounding_words]) + suffix
    )


@register.simple_tag
def get_app_name():
    return apps.get_app_config('main').verbose_name
