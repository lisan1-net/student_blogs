from django import forms
from django.utils.translation import gettext_lazy as _
from django_registration.backends.activation.views import RegistrationView
from django_registration.forms import RegistrationFormUniqueEmail


class FirstLastNamesRegistrationForm(RegistrationFormUniqueEmail):

    first_name = forms.CharField(max_length=150, label=_('First Name'))
    last_name = forms.CharField(max_length=150, label=_('Last Name'))

    def save(self, *args, **kwargs):
        new_user = super().save(*args, **kwargs)
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()
        return new_user


class UniqueEmailRegistrationView(RegistrationView):

    form_class = FirstLastNamesRegistrationForm
