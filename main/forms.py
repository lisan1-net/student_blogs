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

    search_query = forms.CharField(
        max_length=100, min_length=2, label=_('Search query'),
        help_text=_('Enter an expression to search in the texts.')
    )
    search_in_content = forms.BooleanField(
        required=False, initial=True, label=_('Search in content'),
        help_text=_('Search in the content of the texts in addition to the title.')
    )
    blog = forms.ModelChoiceField(
        Blog.objects.all(), required=False, empty_label='', label=_('Blog'), help_text=_('Select a blog to search in.')
    )
    author_name = forms.CharField(
        max_length=150, min_length=2, required=False, label=_('Author name'),
        help_text=_('Enter the name of the author.')
    )
    author_sex = forms.ChoiceField(
        choices=[(None, ''), ('M', _('Male')), ('F', _('Female'))], required=False, label=_('Author sex'),
        help_text=_('Select the sex of the author.')
    )
    author_area = forms.ChoiceField(
        choices=get_author_areas, required=False, label=_('Author area'), help_text=_('Select the area of the author.')
    )
    author_city = forms.ChoiceField(
        choices=get_author_cities, required=False, label=_('Author city'), help_text=_('Select the city of the author.')
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
        help_text=_('Enter the part of the book containing this text.')
    )
    editor = forms.ChoiceField(
        choices=get_editors, required=False, label=_('Editor'), help_text=_('Select the editor of the book.')
    )
    tags = forms.ModelMultipleChoiceField(
        Tag.objects.all(), required=False, widget=widgets.CheckboxSelectMultiple(),
        label=_('Tags'), help_text=_('Select the tags of the text.')
    )
