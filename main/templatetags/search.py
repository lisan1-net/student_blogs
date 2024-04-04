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
    params['search_query'] = word
    params.pop('page', None)
    return reverse('home') + '?' + params.urlencode()


@register.simple_tag
def highlight_range(text: str, start: int | str, end: int | str, pk=None, surrounding_words=5):
    start = int(start)
    end = int(end)
    text_before = text[:start]
    highlighted_text = text[start:end]
    text_after = text[end:]
    words_before = text_before.split(' ')
    words_after = text_after.split(' ')
    prefix = Paginator.ELLIPSIS if len(words_before) > surrounding_words else ''
    suffix = Paginator.ELLIPSIS if len(words_after) > surrounding_words else ''
    generated_before_text = prefix + " ".join(words_before[-surrounding_words:])
    generated_after_text = " ".join(words_after[:surrounding_words]) + suffix
    if pk is not None:
        href = reverse('text', args=[pk]) + f'?start={start}&end={end}'
        onclick = f"window.open('{href}', 'newwindow', 'width=800,height=600'); return false;"
        a = f'<a class="text-warning text-decoration-none" href="{href}" onclick="{onclick}">{highlighted_text}</a>'
        markup = generated_before_text + a + generated_after_text
    else:
        span = f'<span class="text-warning">{highlighted_text}</span>'
        markup = generated_before_text + span + generated_after_text
    return mark_safe(markup)


@register.simple_tag
def get_app_name():
    return apps.get_app_config('main').verbose_name
