from django.urls import path

from main import views

urlpatterns = [
    path('text/<int:pk>/', views.text, name='text'),
    path('', views.home, name='home')
]
