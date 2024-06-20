from django.urls import path, include

from accounts.views import UniqueEmailRegistrationView

urlpatterns = [
    path("register/", UniqueEmailRegistrationView.as_view(), name="django_registration_register"),
    path('', include('django_registration.backends.activation.urls')),
    path('', include('django.contrib.auth.urls')),
]
