from django.urls import path

from main import views

urlpatterns = [
    path('text/<int:pk>/', views.text, name='text'),
    path('words/', views.word_frequencies, name='words'),
    path('', views.home, name='home')
]
