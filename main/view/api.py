from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, reverse
from django.utils.http import content_disposition_header
from django.utils.translation import gettext as _

from main.forms import *
from main.models import Announcement
from main.templatetags.search import get_app_name
from main.utils import *


def blog_ids(request):
    qs = Blog.objects.filter(public=True)
    if request.user.is_authenticated:
        qs = qs | Blog.objects.filter(owner=request.user)
    ids = qs.values_list('id', flat=True)
    return JsonResponse(list(ids), safe=False)


def blog_card(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'main/common/blog_card.html', context={'blog': blog})


def advanced_search_form(request):
    form = SearchForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    return render(request, 'main/search/advanced_search_form.html', context={'form': form})


def announcements(request):
    ancs = Announcement.objects.filter(is_active=True).order_by('-posted_on')
    return render(request, 'main/common/announcements.html', context={'announcements': ancs})


def search_results(request):
    form = SearchForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    results = None
    text_count = None
    if form.is_valid():
        cleaned_data = clean_form_data(form.cleaned_data)
        paginator, text_count, form.advanced = get_search_paginator_and_counts(**cleaned_data)
        results = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/search/search_results.html', context={
        'results': results, 'matched_text_count': text_count, 'form': form,
        'page_url': reverse('home') + request.get_full_path()[len(request.path):],
        'api_url': reverse('search_results')
    })


def export_view(request, form, export_function, filename):
    if form.is_valid():
        cleaned_data = clean_form_data(form.cleaned_data)
        excel_file_content = export_function(**cleaned_data)
        response = HttpResponse(
            excel_file_content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = content_disposition_header(True, filename)
        return response
    return JsonResponse(status=400, data=form.errors, safe=True)


def search_export(request):
    form = SearchForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    return export_view(
        request, form, export_search_results,
        f'{get_app_name()} - {_("Search results")} - {request.GET["search_query"]}.xlsx'
    )


def advanced_vocabulary_form(request):
    form = VocabularyForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    return render(request, 'main/vocabulary/advanced_vocabulary_form.html', context={'form': form})


def vocabulary_form(request):
    form = VocabularyForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    return render(request, 'main/vocabulary/vocabulary_form.html', context={'form': form})


def vocabulary_results(request):
    form = VocabularyForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    page = None
    blog = None
    if form.is_valid():
        blog = form.cleaned_data['blog']
        cleaned_data = clean_form_data(form.cleaned_data)
        paginator = get_vocabulary_paginator(**cleaned_data)
        page = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/vocabulary/vocabulary_results.html', context={
        'frequencies': page, 'blog': blog, 'form': form,
        'page_url': reverse('vocabulary') + request.get_full_path()[len(request.path):],
        'api_url': reverse('vocabulary_results')
    })


def vocabulary_export(request):
    form = VocabularyForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    title = _("Vocabulary results")
    blog_title = get_object_or_404(Blog, pk=int(request.GET["blog"])).title
    return export_view(
        request, form, export_vocabulary_results, f'{get_app_name()} - {title} - {blog_title}.xlsx'
    )


def vocabulary_appearance_progressbar(request, content):
    tokens = content.split(' ')
    form = VocabularyForm(request.GET, user=request.user if request.user.is_authenticated else None)\
        if len(tokens) == 1 else NgramsForm(request.GET, user=request.user if request.user.is_authenticated else None)
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
    form = NgramsForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    return render(request, 'main/ngrams/blog_ngrams_form.html', context={'form': form})


def blog_ngrams_results(request):
    form = NgramsForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    page = None
    blog = None
    if form.is_valid():
        blog = form.cleaned_data['blog']
        cleaned_data = clean_form_data(form.cleaned_data)
        paginator = get_ngrams_paginator(**cleaned_data)
        page = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/ngrams/blog_ngrams_results.html', context={
        'frequencies': page, 'blog': blog, 'form': form,
        'page_url': reverse('blog_ngrams') + request.get_full_path()[len(request.path):],
        'api_url': reverse('blog_ngrams_results')
    })


def ngrams_export(request):
    form = NgramsForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    title = _("Vocabulary results")
    blog_title = get_object_or_404(Blog, pk=int(request.GET["blog"])).title
    return export_view(
        request, form, export_ngram_results, f'{get_app_name()} - {title} - {blog_title}.xlsx'
    )


def blog_comparison_form(request):
    form = BlogComparisonForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    return render(request, 'main/comparison/blog_comparison_form.html', context={'form': form})


def blog_comparison_results(request):
    form = BlogComparisonForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
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
    form = SurroundingWordsFrequencyForm(
        request.GET or None, user=request.user if request.user.is_authenticated else None
    )
    return render(request, 'main/search/advanced_search_form.html', context={'form': form})


def surrounding_words_results(request):
    form = SurroundingWordsFrequencyForm(
        request.GET or None, user=request.user if request.user.is_authenticated else None
    )
    page = None
    fully_indexed = None
    if form.is_valid():
        cleaned_data = clean_form_data(form.cleaned_data)
        paginator, fully_indexed = get_surrounding_words_frequencies_paginator(**cleaned_data)
        page = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/surrounding/surrounding_words_frequency_results.html', context={
        'results': page, 'fully_indexed': fully_indexed, 'form': form,
        'page_url': reverse('surrounding_words') + request.get_full_path()[len(request.path):],
        'api_url': reverse('surrounding_words_results')
    })


def surrounding_words_export(request):
    form = SurroundingWordsFrequencyForm(
        request.GET or None, user=request.user if request.user.is_authenticated else None
    )
    title = _("Surrounding words results")
    return export_view(
        request, form, export_surrounding_words_frequencies_results,
        f'{get_app_name()} - {title} - {request.GET["search_query"]}.xlsx'
    )


def advanced_word_derivations_form(request):
    form = WordDerivationsForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    return render(request, 'main/search/advanced_search_form.html', context={'form': form})


def word_derivations_results(request):
    form = WordDerivationsForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    results = None
    fully_indexed = None
    if form.is_valid():
        cleaned_data = clean_form_data(form.cleaned_data)
        paginator, fully_indexed = get_derivation_frequencies_paginator(**cleaned_data)
        results = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/derivations/word_derivations_results.html', context={
        'results': results, 'fully_indexed': fully_indexed, 'form': form,
        'page_url': reverse('word_derivations') + request.get_full_path()[len(request.path):],
        'api_url': reverse('word_derivations_results')
    })


def word_derivations_export(request):
    form = WordDerivationsForm(request.GET or None, user=request.user if request.user.is_authenticated else None)
    title = _("Word derivations results")
    return export_view(
        request, form, export_derivation_frequencies_results,
        f'{get_app_name()} - {title} - {request.GET["search_query"]}.xlsx'
    )
