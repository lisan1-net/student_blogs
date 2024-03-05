from django.shortcuts import render
from django.db.models import Q

from main.forms import SearchForm
from main.models import *


def home(request):
    form = SearchForm(request.GET or None)
    texts = []
    if form.is_valid():
        search_query = form.cleaned_data['search_query']
        query = Q(title__icontains=search_query)
        if form.cleaned_data['search_in_text']:
            query |= Q(content__icontains=search_query)
        if author_name := form.cleaned_data['author_name']:
            query &= Q(author__name__icontains=author_name)
        if author_sex := form.cleaned_data['author_sex']:
            query &= Q(author__sex=author_sex)
        if author_area := form.cleaned_data['author_area']:
            query &= Q(author__area=author_area)
        if author_city := form.cleaned_data['author_city']:
            query &= Q(author__city=author_city)
        if blog := form.cleaned_data['blog']:
            query &= Q(blog=blog)
        if grade := form.cleaned_data['grade']:
            query &= Q(grade=grade)
        if part := form.cleaned_data['part']:
            query &= Q(part__icontains=part)
        if editor := form.cleaned_data['editor']:
            query &= Q(editor=editor)
        if tags := form.cleaned_data['tags']:
            query &= Q(tags__in=tags)
        texts = Text.objects.filter(query).distinct()
    return render(request, 'main/home.html', context={'form': form, 'texts': texts})
