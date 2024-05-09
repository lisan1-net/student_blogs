from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, reverse

from main.forms import SearchForm
from main.models import Blog, Announcement
from main.utils import get_search_paginator_and_counts, clean_form_data


def blog_ids(request):
    blog_ids = Blog.objects.values_list('id', flat=True)
    return JsonResponse(list(blog_ids), safe=False)


def blog_card(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'main/common/blog_card.html', context={'blog': blog})


def advanced_search_form(request):
    form = SearchForm(request.GET or None)
    return render(request, 'main/search/advanced_search_form.html', context={'form': form})


def announcements(request):
    announcements = Announcement.objects.filter(is_active=True).order_by('-posted_on')
    return render(request, 'main/common/announcements.html', context={'announcements': announcements})


def search_results(request):
    form = SearchForm(request.GET or None)
    results = None
    text_count = None
    if form.is_valid():
        cleaned_data = clean_form_data(form.cleaned_data)
        paginator, text_count, form.advanced = get_search_paginator_and_counts(**cleaned_data)
        results = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/search/search_results.html', context={
        'results': results, 'matched_text_count': text_count, 'page_url': request.get_full_path()[len(request.path):],
        'api_url': reverse('search_results')
    })
