from django.core.paginator import Paginator
from django.db import connections, OperationalError
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import render

from indexes.models import *
from main.forms import *
from main.models import Text
from main.utils import build_common_filter_query


def home(request):
    form = SearchForm(request.GET or None)
    form.advanced = form.is_valid() and any(v for k, v in form.cleaned_data.items() if k != 'search_query')
    return render(request, 'main/search/search.html', context={'form': form})


def text(request, pk):
    text = get_object_or_404(Text, pk=pk)
    return render(request, 'main/popups/text.html', context={'text': text})


def vocabulary(request):
    return render(request, 'main/vocabulary/vocabulary.html')


def search_widget(request):
    response = render(request, 'main/search/search_widget.html')
    response['Content-Security-Policy'] = "frame-ancestors *"  # Allow embedding in any website
    return response


def health_check(request):
    try:
        connections['default'].cursor().execute('SELECT 1')
        return HttpResponse('OK', content_type='text/plain', status=200)
    except OperationalError:
        return HttpResponse('Database not available', content_type='text/plain', status=503)


def blog_ngrams(request):
    ngrams_form = NgramsForm(request.GET or None)
    page = None
    blog = None
    if ngrams_form.is_valid():
        blog = ngrams_form.cleaned_data['blog']
        filter_query = Q(blog=blog)
        q, ngrams_form.advanced = build_common_filter_query(ngrams_form.cleaned_data)
        filter_query &= q
        texts = Text.objects.filter(filter_query).distinct()
        ngram_type = ngrams_form.cleaned_data['ngram_type']
        ngrams = []
        match ngram_type:
            case 'bigram':
                ngrams = Bigram.objects.filter(text__in=texts).prefetch_related('first_token', 'second_token').values(
                    'first_token__content', 'second_token__content'
                ).annotate(frequency=Sum('frequency')).order_by('-frequency').values_list(
                    'first_token__content', 'second_token__content', 'frequency'
                )
            case 'trigram':
                ngrams = Trigram.objects.filter(text__in=texts).prefetch_related(
                    'first_token', 'second_token', 'third_token'
                ).values(
                    'first_token__content', 'second_token__content', 'third_token__content'
                ).annotate(frequency=Sum('frequency')).order_by('-frequency').values_list(
                    'first_token__content', 'second_token__content', 'third_token__content', 'frequency'
                )
        paginator = Paginator(ngrams, 60)
        page = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/ngrams/blog_ngrams.html', context={
        'form': ngrams_form, 'frequencies': page, 'blog': blog
    })


def blog_comparison(request):
    blog_comparison_form = BlogComparisonForm(request.GET or None)
    blogs = None
    if blog_comparison_form.is_valid():
        blogs = blog_comparison_form.cleaned_data['blogs']
    return render(request, 'main/comparison/blog_comparison.html', context={
        'form': blog_comparison_form, 'blogs': blogs
    })
