import re

from django.shortcuts import render
from django.db.models import Q, QuerySet
from django.core.paginator import Paginator


from main.forms import SearchForm
from main.models import *


def home(request):
    form = SearchForm(request.GET or None)
    results = None
    query = None
    advanced_search = False
    in_title_frequency = 0
    in_content_frequency = 0
    texts = Text.objects.none()
    if form.is_valid():
        query = form.cleaned_data['search_query']
        filter_query = Q(title__icontains=query)
        if form.cleaned_data['search_in_content']:
            filter_query |= Q(content__icontains=query)
        if author_name := form.cleaned_data['author_name']:
            filter_query &= Q(author__name__icontains=author_name)
            advanced_search = True
        if author_sex := form.cleaned_data['author_sex']:
            filter_query &= Q(author__sex=author_sex)
            advanced_search = True
        if author_area := form.cleaned_data['author_area']:
            filter_query &= Q(author__area=author_area)
            advanced_search = True
        if author_city := form.cleaned_data['author_city']:
            filter_query &= Q(author__city=author_city)
            advanced_search = True
        if blog := form.cleaned_data['blog']:
            filter_query &= Q(blog=blog)
            advanced_search = True
        if grade := form.cleaned_data['grade']:
            filter_query &= Q(grade=grade)
            advanced_search = True
        if source := form.cleaned_data['source']:
            filter_query &= Q(source=source)
            advanced_search = True
        if part := form.cleaned_data['part']:
            filter_query &= Q(part__icontains=part)
            advanced_search = True
        if editor := form.cleaned_data['editor']:
            filter_query &= Q(editor=editor)
            advanced_search = True
        if tags := form.cleaned_data['tags']:
            filter_query &= Q(tags__in=tags)
            advanced_search = True
        texts = Text.objects.filter(filter_query).distinct()
        results, in_title_frequency, in_content_frequency = find_search_results(
            query, form.cleaned_data['search_in_content'], texts
        )
        results = Paginator(results, 10).get_page(request.GET.get('page'))
        form.advanced = advanced_search
    return render(
        request, 'main/home.html',
        context={'form': form, 'query': query, 'results': results, 'in_title_frequency': in_title_frequency,
                 'in_content_frequency': in_content_frequency, 'matched_text_count': texts.count()}
    )


def find_search_query_position(text: str, query: str, start_index=0) -> tuple[int, int]:
    text = re.sub(r'\s+', ' ', text.lower())
    query = re.sub(r'\s+', ' ', query.lower())
    start = text.find(query, start_index)
    if start == -1:
        return -1, -1
    end = start + len(query)
    return start, end


def find_all_search_query_positions(text: str, query: str) -> list[tuple[int, int]]:
    positions = []
    start = 0
    while start != -1:
        start, end = find_search_query_position(text, query, start)
        if start != -1:
            positions.append((start, end))
            start = end
    return positions


def find_search_results(query: str, search_in_content: bool, texts: QuerySet[Text]) -> tuple[list[dict], int, int]:
    in_title_frequency = 0
    in_content_frequency = 0
    results = []
    for text in texts:
        for positions in find_all_search_query_positions(text.title, query):
            results.insert(
                in_title_frequency,
                {'text': text, 'start': positions[0], 'end': positions[1], 'field': 'title'}
            )
            in_title_frequency += 1
        if search_in_content:
            for positions in find_all_search_query_positions(text.content, query):
                results.append({'text': text, 'start': positions[0], 'end': positions[1], 'field': 'content'})
                in_content_frequency += 1
    return results, in_title_frequency, in_content_frequency
