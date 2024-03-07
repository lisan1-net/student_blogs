from django.shortcuts import render
from django.db.models import Q

from main.forms import SearchForm
from main.models import *


def home(request):
    form = SearchForm(request.GET or None)
    texts = []
    query = None
    if form.is_valid():
        query = form.cleaned_data['search_query']
        filter_query = Q(title__icontains=query)
        if form.cleaned_data['search_in_content']:
            filter_query |= Q(content__icontains=query)
        if author_name := form.cleaned_data['author_name']:
            filter_query &= Q(author__name__icontains=author_name)
        if author_sex := form.cleaned_data['author_sex']:
            filter_query &= Q(author__sex=author_sex)
        if author_area := form.cleaned_data['author_area']:
            filter_query &= Q(author__area=author_area)
        if author_city := form.cleaned_data['author_city']:
            filter_query &= Q(author__city=author_city)
        if blog := form.cleaned_data['blog']:
            filter_query &= Q(blog=blog)
        if grade := form.cleaned_data['grade']:
            filter_query &= Q(grade=grade)
        if source := form.cleaned_data['source']:
            filter_query &= Q(source=source)
        if part := form.cleaned_data['part']:
            filter_query &= Q(part__icontains=part)
        if editor := form.cleaned_data['editor']:
            filter_query &= Q(editor=editor)
        if tags := form.cleaned_data['tags']:
            filter_query &= Q(tags__in=tags)
        texts = Text.objects.filter(filter_query).distinct()
    return render(request, 'main/home.html', context={'form': form, 'texts': texts, 'query': query})
