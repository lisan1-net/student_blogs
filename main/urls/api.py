from django.urls import path

from main.view import api

urlpatterns = [
    path('blog_ids/', api.blog_ids, name='blog_ids'),
    path('blog_card/<int:pk>/', api.blog_card, name='blog_card'),
    path('advanced_search_form/', api.advanced_search_form, name='advanced_search_form'),
    path('announcements/', api.announcements, name='announcements'),
    path('search_results/', api.search_results, name='search_results'),
    path('advanced_vocabulary_form/', api.advanced_vocabulary_form, name='advanced_vocabulary_form'),
    path('vocabulary_form/', api.vocabulary_form, name='vocabulary_form'),
    path('vocabulary_results/', api.vocabulary_results, name='vocabulary_results'),
    path('blog_ngrams_form/', api.blog_ngrams_form, name='blog_ngrams_form'),
    path('blog_ngrams_results/', api.blog_ngrams_results, name='blog_ngrams_results'),
]
