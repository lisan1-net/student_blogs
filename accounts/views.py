from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.utils.translation import gettext_lazy as _
from django_registration.backends.activation.views import RegistrationView
from django_registration.forms import RegistrationFormUniqueEmail
from guardian.shortcuts import assign_perm


class FirstLastNamesRegistrationForm(RegistrationFormUniqueEmail):

    first_name = forms.CharField(max_length=150, label=_('First Name'))
    last_name = forms.CharField(max_length=150, label=_('Last Name'))

    def save(self, *args, **kwargs):
        new_user = super().save(*args, **kwargs)
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()
        assign_perm('main.add_blog', new_user)
        assign_perm('main.add_text', new_user)
        return new_user


class UniqueEmailRegistrationView(RegistrationView):

    form_class = FirstLastNamesRegistrationForm


class UsernameOrEmailAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Username or Email')
        self.fields['username'].widget.attrs['placeholder'] = _('Username or Email')


class UsernameOrEmailLoginView(LoginView):

    form_class = UsernameOrEmailAuthenticationForm
