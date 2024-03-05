from django import forms
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
    return ([(t['editor'], t['editor']) for t in Text.objects.order_by('editor').values('editor').distinct()
             if t['editor']] + [(None, '')])


class SearchForm(forms.Form):

    search_query = forms.CharField(max_length=200)
    search_in_text = forms.BooleanField(required=False, initial=True)
    blog = forms.ModelChoiceField(Blog.objects.all(), required=False, empty_label='')
    author_name = forms.CharField(max_length=150, required=False)
    author_sex = forms.ChoiceField(choices=[(None, ''), ('M', _('Male')), ('F', _('Female'))], required=False)
    author_area = forms.ChoiceField(choices=get_author_areas, required=False)
    author_city = forms.ChoiceField(choices=get_author_cities, required=False)
    grade = forms.ChoiceField(choices=get_grades, required=False)
    part = forms.CharField(max_length=100, required=False)
    editor = forms.ChoiceField(choices=get_editors, required=False)
    tags = forms.ModelMultipleChoiceField(Tag.objects.all(), required=False)
