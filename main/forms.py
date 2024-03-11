from django import forms
from django.forms import widgets
from django.utils.translation import gettext_lazy as _

from main.models import *
from taggit.models import Tag


def get_grades():
    return (
        [(None, '')] +
        [(t['grade'], t['grade']) for t in Text.objects.order_by('grade').values('grade').distinct() if t['grade']]
    )


def get_author_areas():
    return ([(None, '')] +
            [(a['area'], a['area']) for a in Author.objects.order_by('name').values('area').distinct() if a['area']])


def get_author_cities():
    return ([(None, '')] +
            [(c['city'], c['city']) for c in Author.objects.order_by('name').values('city').distinct() if c['city']])


def get_editors():
    return ([(None, '')] +
            [(t['editor'], t['editor']) for t in Text.objects.order_by('editor').values('editor').distinct()
             if t['editor']])


def get_sources():
    return ([(None, '')] +
            [(t['source'], t['source']) for t in Text.objects.order_by('source').values('source').distinct()
             if t['source']])


class SearchForm(forms.Form):

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
        self.fields['search_in_content'].widget.attrs.update({
            'class': 'form-check-input',
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': self.fields['search_in_content'].help_text,
        })
        self.fields['blog'].widget.attrs.update({
            'class': 'form-control',
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': self.fields['blog'].help_text,
        })
        for bound_field in self.author_fields:
            bound_field.field.widget.attrs.update({
                'class': 'form-control',
                'data-toggle': 'tooltip',
                'data-placement': 'top',
                'title': bound_field.field.help_text,
            })
        for bound_field in self.text_fields:
            bound_field.field.widget.attrs.update({
                'class': 'form-control',
                'data-toggle': 'tooltip',
                'data-placement': 'top',
                'title': bound_field.field.help_text,
            })
        self.fields['tags'].widget.attrs.update({
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': self.fields['tags'].help_text,
        })

    @property
    def author_fields(self):
        for field_name in self.fields.keys():
            if field_name.startswith('author_'):
                yield self[field_name]

    @property
    def text_fields(self):
        for field_name in self.fields.keys():
            if field_name in ('source', 'grade', 'part', 'editor'):
                yield self[field_name]

    search_query = forms.CharField(
        max_length=100, min_length=2, label=_('Search query'),
        help_text=_('Enter an expression to search in the texts.'),
    )
    search_in_content = forms.BooleanField(
        required=False, initial=True, label=_('Search in content'),
        help_text=_('Search in the content of the texts in addition to the title.')
    )
    blog = forms.ModelChoiceField(
        Blog.objects.all(), required=False, empty_label='', label=_('Blog'), help_text=_('Select a blog to search in.')
    )
    author_name = forms.CharField(
        max_length=150, min_length=2, required=False, label=_('Name'),
        help_text=_('Enter the name of the author.')
    )
    author_sex = forms.ChoiceField(
        choices=[(None, ''), ('M', _('Male')), ('F', _('Female'))], required=False, label=_('Sex'),
        help_text=_('Select the sex of the author.')
    )
    author_area = forms.ChoiceField(
        choices=get_author_areas, required=False, label=_('Area'), help_text=_('Select the area of the author.')
    )
    author_city = forms.ChoiceField(
        choices=get_author_cities, required=False, label=_('City'), help_text=_('Select the city of the author.')
    )
    source = forms.ChoiceField(
        choices=get_sources, required=False, label=_('Source'), help_text=_('Select the source of the text.')
    )
    grade = forms.ChoiceField(
        choices=get_grades, required=False, label=_('Grade'),
        help_text=_('Select the grade of the student studying this text.')
    )
    part = forms.CharField(
        max_length=100, required=False, label=_('Part'),
        help_text=_('Enter the title of the book part containing this text.')
    )
    editor = forms.ChoiceField(
        choices=get_editors, required=False, label=_('Editor'), help_text=_('Select the editor of the book.')
    )
    tags = forms.ModelMultipleChoiceField(
        Tag.objects.all(), required=False, widget=widgets.CheckboxSelectMultiple,
        label=_('Tags'), help_text=_('Select the tags of the text.')
    )
