import re
from functools import lru_cache
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import *

from django import template
from django.apps import apps
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Length
from django.template.defaultfilters import mark_safe, floatformat
from django.urls import reverse
from django.utils.html import escape
from django.utils.text import slugify

from indexes.utils import separate_tags_positions_and_text
from main.models import TextToken, DictionaryDefinition, SemanticTag, MorphologicalTag
from main.utils import get_context

register = template.Library()


@register.filter
def slugify_unicode(text):
    return slugify(text, allow_unicode=True)


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
    def replace_newlines(match):
        # If the matched string is a newline character inside an attribute, return <br>
        if match.group(1) is not None:
            return '<br>'
        # Otherwise, return it replaced with '</p><p>'
        else:
            return '</p><p>'

    # Use a regular expression to replace newline characters that are not inside attributes
    content = re.sub(r'("[^"]*\\n[^"]*")|(\\n)', replace_newlines, content)
    return mark_safe('<p>' + content + '</p>')


@register.filter
def url_with_page(url, page):
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    params['page'] = page
    return parsed_url._replace(query=urlencode(params, doseq=True)).geturl()


@register.simple_tag
def search_url(request, word, blog_pk=None):
    params = request.GET.copy()
    params['search_query'] = f'"{word}"'
    if blog_pk is not None:
        params['blog'] = blog_pk
    params.pop('page', None)
    return reverse('home') + '?' + params.urlencode()


@register.filter
def percent(value, unlocalized=False):
    if value is None:
        return None
    return floatformat(value * 100.0, 2 if not unlocalized else "2u") + '%'


@register.simple_tag
def highlight_range(text: str, highlight_start=None, highlight_end=None, pk=None, surrounding_words=5, link=True):
    text_without_custom_tags = replace_custom_tags_with_popovers(text)
    if isinstance(highlight_start, str) and highlight_start.isdigit():
        highlight_start = int(highlight_start)
    elif highlight_start is None:
        highlight_start = 0
    if isinstance(highlight_end, str) and highlight_end.isdigit():
        highlight_end = int(highlight_end)
    elif highlight_end is None:
        highlight_end = len(text_without_custom_tags)
    text_before, highlighted_text, text_after, visible_words_before, visible_words_after, prefix, suffix = get_context(
        text_without_custom_tags, highlight_start, highlight_end, surrounding_words
    )

    def get_generated_text(words: list[str], prefix='', suffix=''):
        return prefix + ' '.join(words) + suffix

    generated_before_text = get_generated_text(visible_words_before, prefix=prefix)
    generated_after_text = get_generated_text(visible_words_after, suffix=suffix)

    definitions_start = highlight_start - len(generated_before_text) + len(prefix)
    definitions_end = highlight_end + len(generated_after_text)
    positions_definitions = get_definitions(pk, definitions_start, definitions_end)

    def close_indexes(pos_defs: dict, indexes: tuple[int, int], margin=3):
        for pos_idx in pos_defs.keys():
            start_diff = abs(pos_idx[0] - indexes[0])
            end_diff = abs(pos_idx[1] - indexes[1])
            pos_range = pos_idx[1] - pos_idx[0]
            indexes_range = indexes[1] - indexes[0]
            if start_diff <= margin and end_diff <= margin and pos_range == indexes_range:
                return pos_idx
        return None

    def add_popovers(words: Iterable[str], start: int, pos_defs: dict):
        popover_words = []
        for word in words:
            end = start + len(word)
            if found_indexes := close_indexes(pos_defs, (start, end)):
                terms_definitions = pos_defs[found_indexes]
                popover_words.append(
                    wrap_with_popover(
                        word, '\n\n'.join(terms_definitions[y]['definition'] for y in range(len(terms_definitions)))
                    )
                )
            else:
                popover_words.append(word)
            start = end + 1
            if found_indexes:
                start = found_indexes[1] + 1
        return popover_words

    visible_words_before = add_popovers(map(escape, visible_words_before), definitions_start, positions_definitions)
    highlighted_text = ' '.join(add_popovers(escape(highlighted_text).split(' '), len(text_before) + 1, positions_definitions))
    visible_words_after = add_popovers(
        map(escape, visible_words_after), len(text_before) + len(highlighted_text) + 2, positions_definitions
    )

    if link and pk is not None:
        href = reverse('text', args=[pk]) + f'?start={highlight_start}&end={highlight_end}'
        onclick = f"window.open('{href}', 'newwindow', 'width=800,height=500'); return false;"
        a = f'<a class="text-warning text-decoration-none" href="{href}" onclick="{onclick}">{highlighted_text}</a>'
        markup = (get_generated_text(visible_words_before, prefix=prefix)
                  + a +
                  get_generated_text(visible_words_after, suffix=suffix))
    else:
        span = f'<span class="text-warning">{highlighted_text}</span>'
        if text_before or text_after:
            markup = (get_generated_text(visible_words_before, prefix=prefix)
                      + span +
                      get_generated_text(visible_words_after, suffix=suffix))
        else:
            markup = highlighted_text
    return mark_safe(markup)


@register.simple_tag
def get_app_name():
    return apps.get_app_config('main').verbose_name


@lru_cache(64)
def get_definitions(text_pk, start, end):
    text_tokens = TextToken.objects.filter(text_id=text_pk, start__gte=start, end__lte=end).annotate(
        length=Length('token__content')
    ).filter(length__gte=3)
    positions_definitions = {}
    for text_token in text_tokens:
        definitions = DictionaryDefinition.objects.annotate(
            length=Length('term')
        ).filter(
            Q(term__startswith=text_token.token.content) | Q(term__endswith=text_token.token.content)
        ).values('term', 'definition')
        if definitions.exists():
            positions_definitions[(text_token.start, text_token.end)] = definitions
    return positions_definitions


@register.filter
def replace_custom_tags_with_popovers(text: str):
    tag_merger = TagMerger()
    tag_merger.feed(text)
    text = ''.join(tag_merger.result)
    tags_pos, text = separate_tags_positions_and_text(text)
    insertion_offset = 0
    for (open_index, open_tag), (close_index, close_tag) in zip(tags_pos[:-1], tags_pos[1:]):
        tag_symbols = open_tag.strip('<>').split('|')
        tags = SemanticTag.objects.filter(symbol__in=tag_symbols).union(
            MorphologicalTag.objects.filter(symbol__in=tag_symbols)
        )
        if tags.exists():
            popover_content = '\n\n'.join(f'{tag.content}' for tag in tags)
            tag_text = text[open_index + insertion_offset:close_index + insertion_offset]
            popover_span = wrap_with_popover(tag_text, popover_content, wrap_element='b')
            text = text[:open_index + insertion_offset] + popover_span + text[close_index + insertion_offset:]
            insertion_offset += len(popover_span) - len(tag_text)
    return mark_safe(text)


@lru_cache(64)
def wrap_with_popover(title: str, content: str, wrap_element='u'):
    return (
        '<span data-toggle="popover" data-trigger="hover" title="{title}" data-content="{content}" tabindex="0" '
        'data-html="true" data-boundary="viewport"><{wrap_element}>{title}</{wrap_element}></span>'
    ).format(
        title=escape(title), wrap_element=escape(wrap_element),
        content='<ul>' + ''.join(f'<li>{escape(part)}</li>' for part in content.split('\n\n')) + '</ul>',
    )


class TagMerger(HTMLParser):

    def __init__(self):
        super().__init__()
        self._result = []
        self.level = 0

    def handle_starttag(self, tag, attrs):
        if attrs:
            return
        if self.level == 0:
            self._result.append('<' + tag + '>')
        else:
            self._result[-1] = self._result[-1][:-1] + '|' + tag + '>'
        self.level += 1

    def handle_endtag(self, tag):
        self.level -= 1
        if '</' in self._result[-1]:
            self._result[-1] = self._result[-1][:-1] + '|' + tag + '>'
        else:
            self._result[-1] += '</' + tag + '>'

    def handle_data(self, data):
        if self.level == 0:
            self._result.append(data)
        else:
            self._result[-1] += data

    @property
    def result(self):
        result = []
        for item in self._result:
            if '</' in item:
                close_tag = item[item.index('</'):]
                tag_names = reversed(close_tag.strip('</>').split('|'))
                close_tag = '</' + '|'.join(tag_names) + '>'
                item = item[:-len(close_tag)] + close_tag
            result.append(item)
        return result
