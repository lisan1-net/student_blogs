from django.http import JsonResponse
from django.shortcuts import render, reverse

from main.forms import *
from main.models import Announcement
from main.utils import *


def blog_ids(request):
    ids = Blog.objects.values_list('id', flat=True)
    return JsonResponse(list(ids), safe=False)


def blog_card(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'main/common/blog_card.html', context={'blog': blog})


def advanced_search_form(request):
    form = SearchForm(request.GET or None)
    return render(request, 'main/search/advanced_search_form.html', context={'form': form})


def announcements(request):
    ancs = Announcement.objects.filter(is_active=True).order_by('-posted_on')
    return render(request, 'main/common/announcements.html', context={'announcements': ancs})


def search_results(request):
    form = SearchForm(request.GET or None)
    results = None
    text_count = None
    if form.is_valid():
        cleaned_data = clean_form_data(form.cleaned_data)
        paginator, text_count, form.advanced = get_search_paginator_and_counts(**cleaned_data)
        results = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/search/search_results.html', context={
        'results': results, 'matched_text_count': text_count,
        'page_url': reverse('home') + request.get_full_path()[len(request.path):],
        'api_url': reverse('search_results')
    })


def advanced_vocabulary_form(request):
    form = VocabularyForm(request.GET or None)
    return render(request, 'main/vocabulary/advanced_vocabulary_form.html', context={'form': form})


def vocabulary_form(request):
    form = VocabularyForm(request.GET or None)
    return render(request, 'main/vocabulary/vocabulary_form.html', context={'form': form})


def vocabulary_results(request):
    form = VocabularyForm(request.GET or None)
    page = None
    blog = None
    if form.is_valid():
        blog = form.cleaned_data['blog']
        cleaned_data = clean_form_data(form.cleaned_data)
        paginator = get_vocabulary_paginator(**cleaned_data)
        page = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/vocabulary/vocabulary_results.html', context={
        'frequencies': page, 'blog': blog,
        'page_url': reverse('vocabulary') + request.get_full_path()[len(request.path):],
        'api_url': reverse('vocabulary_results')
    })


def vocabulary_appearance_progressbar(request, content):
    tokens = content.split(' ')
    form = VocabularyForm(request.GET) if len(tokens) == 1 else NgramsForm(request.GET)
    ratio = None
    if form.is_valid():
        filter_q, _ = build_common_filter_query(form.cleaned_data)
        texts = Text.objects.filter(filter_q)
        match len(tokens):
            case 1:
                ratio = texts.filter(tokens__content=tokens[0]).distinct().count() / texts.count()
            case 2:
                ratio = texts.filter(
                    bigrams__first_token__content=tokens[0], bigrams__second_token__content=tokens[1]
                ).distinct().count() / texts.count()
            case 3:
                ratio = texts.filter(
                    trigrams__first_token__content=tokens[0], trigrams__second_token__content=tokens[1],
                    trigrams__third_token__content=tokens[2]
                ).distinct().count() / texts.count()
    context = {'ratio': ratio, 'word': content, 'color': request.GET.get('color')}
    return render(
        request, 'main/vocabulary/appearance_ratio_progressbar.html', context=context
    )


def blog_ngrams_form(request):
    form = NgramsForm(request.GET or None)
    return render(request, 'main/ngrams/blog_ngrams_form.html', context={'form': form})


def blog_ngrams_results(request):
    form = NgramsForm(request.GET or None)
    page = None
    blog = None
    if form.is_valid():
        blog = form.cleaned_data['blog']
        cleaned_data = clean_form_data(form.cleaned_data)
        paginator = get_ngrams_paginator(**cleaned_data)
        page = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/ngrams/blog_ngrams_results.html', context={
        'frequencies': page, 'blog': blog,
        'page_url': reverse('blog_ngrams') + request.get_full_path()[len(request.path):],
        'api_url': reverse('blog_ngrams_results')
    })


def blog_comparison_form(request):
    form = BlogComparisonForm(request.GET or None)
    return render(request, 'main/comparison/blog_comparison_form.html', context={'form': form})


def blog_comparison_results(request):
    form = BlogComparisonForm(request.GET or None)
    blogs = None
    if form.is_valid():
        blogs = form.cleaned_data['blogs']
    return render(request, 'main/comparison/blog_comparison_results.html', context={'blogs': blogs})


def most_frequent_words(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    return render(request, 'main/comparison/most_frequent_words.html', context={'blog': blog})


def most_frequent_bigrams(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    return render(request, 'main/comparison/most_frequent_bigrams.html', context={'blog': blog})


def most_frequent_trigrams(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    return render(request, 'main/comparison/most_frequent_trigrams.html', context={'blog': blog})


def advanced_surrounding_words_form(request):
    form = SurroundingWordsFrequencyForm(request.GET or None)
    return render(request, 'main/search/advanced_search_form.html', context={'form': form})


def surrounding_words_results(request):
    form = SurroundingWordsFrequencyForm(request.GET or None)
    page = None
    fully_indexed = None
    if form.is_valid():
        cleaned_data = clean_form_data(form.cleaned_data)
        paginator, fully_indexed = get_surrounding_words_frequencies_paginator(**cleaned_data)
        page = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/surrounding/surrounding_words_frequency_results.html', context={
        'results': page, 'fully_indexed': fully_indexed,
        'page_url': reverse('surrounding_words') + request.get_full_path()[len(request.path):],
        'api_url': reverse('surrounding_words_results')
    })


def advanced_word_derivations_form(request):
    form = WordDerivationsForm(request.GET or None)
    return render(request, 'main/search/advanced_search_form.html', context={'form': form})


def word_derivations_results(request):
    form = WordDerivationsForm(request.GET or None)
    results = None
    fully_indexed = None
    if form.is_valid():
        cleaned_data = clean_form_data(form.cleaned_data)
        paginator, fully_indexed = get_derivation_frequencies_paginator(**cleaned_data)
        results = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/derivations/word_derivations_results.html', context={
        'results': results, 'fully_indexed': fully_indexed,
        'page_url': reverse('word_derivations') + request.get_full_path()[len(request.path):],
        'api_url': reverse('word_derivations_results')
    })
