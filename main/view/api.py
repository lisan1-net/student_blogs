from django.http import JsonResponse
from django.shortcuts import render, reverse

from main.forms import *
from main.models import Blog, Announcement
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
