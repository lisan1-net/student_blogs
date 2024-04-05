from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db import connections

from indexes.models import TextWord
from indexes.utils import normalize
from main.forms import SearchForm, VocabularyForm
from main.models import Text, Blog
from main.utils import find_search_results


def build_common_filter_query(form: SearchForm):
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


def home(request):
    form = SearchForm(request.GET or None)
    results = None
    query = None
    in_content_frequency = 0
    matched_texts_count = None
    if form.is_valid():
        filter_query = build_common_filter_query(form)
        if blog := form.cleaned_data['blog']:
            filter_query &= Q(blog=blog)
            form.advanced = True
        query = normalize(form.cleaned_data['search_query'])
        texts = Text.objects.filter(filter_query).distinct()
        results, in_content_frequency = find_search_results(query, texts)
        matched_texts_count = len(set(r['text'] for r in results))
        results = Paginator(results, 10).get_page(request.GET.get('page'))
    return render(
        request, 'main/search/search.html',
        context={'form': form, 'query': query, 'results': results, 'frequency': in_content_frequency,
                 'matched_text_count': matched_texts_count, 'blogs': Blog.objects.all()}
    )


def text(request, pk):
    text = get_object_or_404(Text, pk=pk)
    return render(request, 'main/popups/text.html', context={'text': text})


def vocabulary(request):
    vocabulary_form = VocabularyForm(request.GET or None)
    page = None
    if vocabulary_form.is_valid():
        filter_query = Q(blog=vocabulary_form.cleaned_data['blog'])
        filter_query &= build_common_filter_query(vocabulary_form)
        texts = Text.objects.filter(filter_query).distinct()
        word_frequencies = TextWord.objects.filter(text__in=texts, word__part='STEM').values('word__content').annotate(
            frequency=Count('word__content')
        ).order_by('-frequency').values_list('word__content', 'frequency')
        paginator = Paginator(word_frequencies, 60)
        page = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/vocabulary/vocabulary.html', context={'form': vocabulary_form, 'frequencies': page})


def search_widget(request):
    response = render(request, 'main/search/search_widget.html')
    response['Content-Security-Policy'] = "frame-ancestors *"  # Allow embedding in any website
    return response


def health_check(request):
    connections['default'].cursor().execute('SELECT 1')
    return HttpResponse('OK', content_type='text/plain', status=200)
