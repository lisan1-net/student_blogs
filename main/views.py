from collections import Counter

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from main.forms import SearchForm
from main.models import *
from main.utils import find_search_results, split_words


def home(request):
    form = SearchForm(request.GET or None)
    results = None
    query = None
    advanced_search = False
    in_content_frequency = 0
    matched_texts_count = None
    if form.is_valid():
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
        if blog := form.cleaned_data['blog']:
            filter_query &= Q(blog=blog)
            advanced_search = True
        if type_ := form.cleaned_data['type']:
            filter_query &= Q(type=type_)
            advanced_search = True
        if tags := form.cleaned_data['tags']:
            filter_query &= Q(tags__in=tags)
            advanced_search = True
        query = form.cleaned_data['search_query']
        texts = Text.objects.filter(filter_query).distinct()
        results, in_content_frequency = find_search_results(query, texts)
        matched_texts_count = len(set(r['text'] for r in results))
        results = Paginator(results, 10).get_page(request.GET.get('page'))
        form.advanced = advanced_search
    return render(
        request, 'main/home.html',
        context={'form': form, 'query': query, 'results': results, 'frequency': in_content_frequency,
                 'matched_text_count': matched_texts_count}
    )


def text(request, pk):
    text = get_object_or_404(Text, pk=pk)
    return render(request, 'main/text.html', context={'text': text})


def word_frequencies(request):
    frequencies = Counter()
    for text in Text.objects.all():
        frequencies.update(split_words(text.content_normalized))
    paginator = Paginator(frequencies.most_common(len(frequencies.keys())), 60)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/words.html', context={'frequencies': page})
