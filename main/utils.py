import re
from functools import lru_cache
from typing import Iterable

from django.db.models import Q
from pyarabic.araby import DIACRITICS

from indexes.utils import normalize


@lru_cache(64)
def get_diacritics_insensitive_regexp(query: str) -> re.Pattern:
    query = normalize(query)
    return re.compile(''.join(fr'{letter}[{"".join(DIACRITICS)}]*' for letter in query), re.IGNORECASE)


def find_search_query_position(text: str, query: str, start_index=0) -> tuple[int, int]:
    start = -1
    end = -1
    if query.startswith('"') and query.endswith('"'):
        query = query[1:-1]
        match = re.search(fr'\b{get_diacritics_insensitive_regexp(query).pattern}\b', text[start_index:])
        if match:
            start = match.start() + start_index
            end = match.end() + start_index
    else:
        match = re.search(get_diacritics_insensitive_regexp(query), text[start_index:])
        if match:
            start = match.start() + start_index
            end = match.end() + start_index
    return start, end


@lru_cache(128)
def find_all_search_query_positions(text: str, query: str) -> list[tuple[int, int]]:
    positions = []
    start = 0
    while start != -1:
        start, end = find_search_query_position(text, query, start)
        if start != -1:
            positions.append((start, end))
            start = end
    return positions


@lru_cache(64)
def find_search_results(query: str, texts: Iterable) -> tuple[list[dict], int]:
    in_content_frequency = 0
    results = []
    for text in texts:
        for positions in find_all_search_query_positions(text.content, query):
            results.append({'text': text, 'start': positions[0], 'end': positions[1]})
            in_content_frequency += 1
    return results, in_content_frequency


def build_common_filter_query(form):
    advanced_search = False
    filter_query = Q()
    if student_number := form.cleaned_data['student_number']:
        filter_query &= Q(student_number=student_number)
        advanced_search = True
    if sex := form.cleaned_data['sex']:
        filter_query &= Q(sex=sex)
        advanced_search = True
    if level := form.cleaned_data['level']:
        filter_query &= Q(level=level)
        advanced_search = True
    if city := form.cleaned_data['city']:
        filter_query &= Q(city=city)
        advanced_search = True
    if school := form.cleaned_data['school']:
        filter_query &= Q(school=school)
        advanced_search = True
    if type_ := form.cleaned_data['type']:
        filter_query &= Q(type=type_)
        advanced_search = True
    if source_type := form.cleaned_data['source_type']:
        filter_query &= Q(source_type=source_type)
        advanced_search = True
    if author_name := form.cleaned_data['author_name']:
        filter_query &= Q(author_name__icontains=author_name)
        advanced_search = True
    if tags := form.cleaned_data['tags']:
        filter_query &= Q(tags__in=tags)
        advanced_search = True
    form.advanced = advanced_search
    return filter_query
