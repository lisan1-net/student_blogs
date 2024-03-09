from django.shortcuts import render
from django.db.models import Q

from main.forms import SearchForm
from main.models import *


def home(request):
    form = SearchForm(request.GET or None)
    texts = []
    query = None
    advanced_search = False
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
        form.advanced = advanced_search
    return render(
        request, 'main/home.html',
        context={'form': form, 'texts': texts, 'query': query}
    )
