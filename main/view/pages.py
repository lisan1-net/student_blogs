from django.db import connections, OperationalError
from django.http import HttpResponse
from django.shortcuts import render

from main.forms import *
from main.models import Text


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
    return render(request, 'main/ngrams/blog_ngrams.html')


def blog_comparison(request):
    return render(request, 'main/comparison/blog_comparison.html')
