from django.urls import path

from main import views

urlpatterns = [
    path('text/<int:pk>/', views.text, name='text'),
    path('words/', views.vocabulary, name='vocabulary'),
    path('search_widget/', views.search_widget, name='search_widget'),
    path('', views.home, name='home')
]
