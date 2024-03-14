from django import forms
from django.forms import widgets
from django.utils.translation import gettext_lazy as _

from main.models import *
from taggit.models import Tag


def get_schools():
    return Text.objects.values_list('school', flat=True).distinct()


def get_cities():
    return Text.objects.values_list('city', flat=True).distinct()


class SearchForm(forms.ModelForm):

    class Meta:

        @staticmethod
        def formfield_for_dbfield(db_field, required=False, **kwargs):
            if isinstance(db_field, models.IntegerField):
                kwargs['min_value'] = 1
            if db_field.name == 'school':
                kwargs['widget'] = widgets.Select(choices=[(None, '')] + [(s, s) for s in get_schools()])
            elif db_field.name == 'city':
                kwargs['widget'] = widgets.Select(choices=[(None, '')] + [(c, c) for c in get_cities()])
            form_field = db_field.formfield(required=required, **kwargs)
            if form_field:
                form_field.widget.attrs.update({
                    'class': 'form-control',
                    'data-toggle': 'tooltip',
                    'data-placement': 'top',
                    'title': db_field.help_text,
                    'autocomplete': 'off',
                })
                return form_field

        model = Text
        exclude = ['title', 'content', 'tags']
        formfield_callback = formfield_for_dbfield

    template_name = 'main/parts/search_form.html'
    error_css_class = 'is-invalid'

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['search_query'].widget.attrs.update({
            'placeholder': self.fields['search_query'].help_text,
            'class': 'form-control form-control-lg',
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': self.fields['search_query'].help_text,
        })
        self.fields['blog'].empty_label = ''
        self.fields['tags'].widget.attrs.update({
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': self.fields['tags'].help_text,
        })

    search_query = forms.CharField(
        max_length=100, min_length=2, label=_('Search query'),
        help_text=_('Enter an expression to search in the texts. Any expression in double quotes will be searched as a '
                    'whole word.')
    )

    tags = forms.ModelMultipleChoiceField(
        Tag.objects.all(), required=False, widget=widgets.CheckboxSelectMultiple,
        label=_('Tags'), help_text=_('Select the tags of the text.')
    )

    @property
    def text_fields(self):
        for field in self.fields:
            if field in ('search_query', 'blog', 'tags'):
                continue
            yield self[field]

    def clean(self):
        cleaned_data = super(SearchForm, self).clean()
        for k, v in cleaned_data.items():
            if isinstance(self.fields[k], forms.CharField):
                cleaned_data[k] = normalize(v)
        return cleaned_data
