from django.urls import path

from main import views

urlpatterns = [
    path('text/<int:pk>/', views.text, name='text'),
    path('words/', views.vocabulary, name='vocabulary'),
    path('blog_ngrams/', views.blog_ngrams, name='blog_ngrams'),
    path('search_widget/', views.search_widget, name='search_widget'),
    path('healthz/', views.health_check, name='health_check'),
    path('', views.home, name='home')
]
