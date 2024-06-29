from django.urls import path, include

from accounts.views import UniqueEmailRegistrationView, UsernameOrEmailLoginView

urlpatterns = [
    path("register/", UniqueEmailRegistrationView.as_view(), name="django_registration_register"),
    path('', include('django_registration.backends.activation.urls')),
    path("login/", UsernameOrEmailLoginView.as_view(), name="login"),
    path('', include('django.contrib.auth.urls')),
]
