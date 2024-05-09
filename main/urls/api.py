from django.urls import path

from main.view import api

urlpatterns = [
    path('blog_ids/', api.blog_ids, name='blog_ids'),
    path('blog_card/<int:pk>/', api.blog_card, name='blog_card'),
    path('advanced_search_form/', api.advanced_search_form, name='advanced_search_form'),
    path('announcements/', api.announcements, name='announcements'),
    path('search_results/', api.search_results, name='search_results')
]
