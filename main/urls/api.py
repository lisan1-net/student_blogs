from django.urls import path

from main.view import api

urlpatterns = [
    path('blog_ids/', api.blog_ids, name='blog_ids'),
    path('blog_card/<int:pk>/', api.blog_card, name='blog_card'),
]
