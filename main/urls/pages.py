from django.urls import path

from main.view import pages

urlpatterns = [
    path('text/<int:pk>/', pages.text, name='text'),
    path('blog/<int:pk>/', pages.blog, name='blog'),
    path('words/', pages.vocabulary, name='vocabulary'),
    path('blog_ngrams/', pages.blog_ngrams, name='blog_ngrams'),
    path('blog_comparison/', pages.blog_comparison, name='blog_comparison'),
    path('surrounding_words/', pages.surrounding_words, name='surrounding_words'),
    path('word_derivations/', pages.word_derivations, name='word_derivations'),
    path('search_widget/', pages.search_widget, name='search_widget'),
    path('healthz/', pages.health_check, name='health_check'),
    path('', pages.home, name='home')
]
