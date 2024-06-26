from django.urls import path

from main.view import api

urlpatterns = [
    path('blog_ids/', api.blog_ids, name='blog_ids'),
    path('blog_card/<int:pk>/', api.blog_card, name='blog_card'),
    path('advanced_search_form/', api.advanced_search_form, name='advanced_search_form'),
    path('announcements/', api.announcements, name='announcements'),
    path('search_results/', api.search_results, name='search_results'),
    path('search_export', api.search_export, name='search_export'),
    path('advanced_vocabulary_form/', api.advanced_vocabulary_form, name='advanced_vocabulary_form'),
    path('vocabulary_form/', api.vocabulary_form, name='vocabulary_form'),
    path('vocabulary_results/', api.vocabulary_results, name='vocabulary_results'),
    path('vocabulary_export', api.vocabulary_export, name='vocabulary_export'),
    path('vocabulary_appearance_progressbar/<str:content>/', api.vocabulary_appearance_progressbar,
         name='vocabulary_appearance_progressbar'),
    path('blog_ngrams_form/', api.blog_ngrams_form, name='blog_ngrams_form'),
    path('blog_ngrams_results/', api.blog_ngrams_results, name='blog_ngrams_results'),
    path('ngrams_export', api.ngrams_export, name='ngrams_export'),
    path('blog_comparison_form/', api.blog_comparison_form, name='blog_comparison_form'),
    path('blog_comparison_results/', api.blog_comparison_results, name='blog_comparison_results'),
    path('most_frequent_words/<int:blog_id>/', api.most_frequent_words, name='most_frequent_words'),
    path('most_frequent_bigrams/<int:blog_id>/', api.most_frequent_bigrams, name='most_frequent_bigrams'),
    path('most_frequent_trigrams/<int:blog_id>/', api.most_frequent_trigrams, name='most_frequent_trigrams'),
    path('advanced_surrounding_words_form/', api.advanced_surrounding_words_form, name='advanced_surrounding_words_form'),
    path('surrounding_words_results/', api.surrounding_words_results, name='surrounding_words_results'),
    path('surrounding_words_export', api.surrounding_words_export, name='surrounding_words_export'),
    path('advanced_word_derivations_form/', api.advanced_word_derivations_form, name='advanced_word_derivations_form'),
    path('word_derivations_results/', api.word_derivations_results, name='word_derivations_results'),
    path('word_derivations_export/', api.word_derivations_export, name='word_derivations_export')
]
