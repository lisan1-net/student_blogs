from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from main.forms import SearchForm
from main.models import *
from main.utils import find_search_results


def home(request):
    form = SearchForm(request.GET or None)
    results = None
    query = None
    advanced_search = False
    in_title_frequency = 0
    in_content_frequency = 0
    texts = set()
    if form.is_valid():
        filter_query = Q()
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
        query = form.cleaned_data['search_query']
        for text in Text.objects.filter(filter_query).distinct():
            if text not in texts:
                if query in text.title_normalized:
                    texts.add(text)
                elif form.cleaned_data['search_in_content'] and query in text.content_normalized:
                    texts.add(text)
        results, in_title_frequency, in_content_frequency = find_search_results(
            query, form.cleaned_data['search_in_content'], texts
        )
        results = Paginator(results, 10).get_page(request.GET.get('page'))
        form.advanced = advanced_search
    return render(
        request, 'main/home.html',
        context={'form': form, 'query': query, 'results': results, 'in_title_frequency': in_title_frequency,
                 'in_content_frequency': in_content_frequency, 'matched_text_count': len(texts)}
    )


def text(request, pk):
    text = get_object_or_404(Text, pk=pk)
    return render(request, 'main/text.html', context={'text': text})
