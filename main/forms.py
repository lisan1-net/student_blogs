from functools import partial

from django import forms
from django.conf import settings
from django.db import models
from django.forms import widgets
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from taggit.models import Tag

from indexes.utils import normalize
from main.models import Blog, Text


def get_schools(user=None):
    queryset = Text.objects.filter(blog__public=True)
    if user:
        queryset = queryset | Text.objects.filter(blog__owner=user)
    return queryset.values_list('school', 'school').distinct().order_by('school')


def get_cities(user=None):
    queryset = Text.objects.filter(blog__public=True)
    if user:
        queryset = queryset | Text.objects.filter(blog__owner=user)
    return queryset.values_list('city', 'city').distinct().order_by('city')


def with_empty(choices_function):
    def wrapper():
        choices = list(map(lambda x: (None, '') if x[0] is None else x, choices_function()))
        if all(map(lambda x: x[0], choices)):
            choices.insert(0, (None, ''))
        return choices
    return wrapper


def get_blogs(user=None):
    queryset = Blog.objects.filter(public=True)
    if user:
        queryset = queryset | user.blog_set.all()
    for _id, title in queryset.values_list('id', 'title').order_by('title'):
        yield _id, title


def get_source_types(user=None):
    queryset = Text.objects.filter(blog__public=True)
    if user:
        queryset = queryset | Text.objects.filter(blog__owner=user)
    return queryset.values_list('source_type', 'source_type').distinct().order_by('source_type')


def get_author_names(user=None):
    queryset = Text.objects.filter(blog__public=True)
    if user:
        queryset = queryset | Text.objects.filter(blog__owner=user)
    return queryset.values_list('author_name', 'author_name').distinct().order_by('author_name')


class SearchForm(forms.ModelForm):

    class Meta:

        @staticmethod
        def formfield_for_dbfield(db_field, required=False, **kwargs):
            if isinstance(db_field, models.IntegerField):
                kwargs['min_value'] = 1
            match db_field.name:
                case 'school':
                    form_field = forms.ChoiceField(choices=with_empty(get_schools), required=required,
                                                   label=db_field.verbose_name, help_text=db_field.help_text)
                case 'city':
                    form_field = forms.ChoiceField(choices=with_empty(get_cities), required=required,
                                                   label=db_field.verbose_name, help_text=db_field.help_text)
                case 'blog':
                    form_field = forms.ChoiceField(choices=with_empty(get_blogs), required=required,
                                                   label=db_field.verbose_name, help_text=db_field.help_text)
                case 'source_type':
                    form_field = forms.ChoiceField(choices=with_empty(get_source_types), required=required,
                                                   label=db_field.verbose_name, help_text=db_field.help_text)
                case 'author_name':
                    form_field = forms.ChoiceField(choices=with_empty(get_author_names), required=required,
                                                   label=db_field.verbose_name, help_text=db_field.help_text)
                case other:
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

    template_name = 'main/search/search_form.html'
    error_css_class = 'is-invalid'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
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
        self.fields['export_count'].widget.attrs.update({
            'class': 'form-control',
            'title': self.fields['export_count'].help_text,
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'value': self.fields['export_count'].initial
        })
        if user:
            self.fields['blog'].choices = with_empty(partial(get_blogs, user))()
            self.fields['school'].choices = with_empty(partial(get_schools, user))()
            self.fields['city'].choices = with_empty(partial(get_cities, user))()
            self.fields['source_type'].choices = with_empty(partial(get_source_types, user))()
            self.fields['author_name'].choices = with_empty(partial(get_author_names, user))()

    search_query = forms.CharField(
        max_length=100, min_length=2, label=_('Search query'),
        help_text=_('Enter an expression to search in the texts. Any expression in double quotes will be searched as a '
                    'whole word.')
    )

    tags = forms.ModelMultipleChoiceField(
        Tag.objects.all(), required=False, widget=widgets.CheckboxSelectMultiple,
        label=_('Tags'), help_text=_('Select the tags of the text.')
    )

    export_count = forms.IntegerField(
        label=_('Export count'), help_text=_('The maximum number of results to export.'), min_value=1,
        max_value=settings.EXPORT_LIMIT, required=False, initial=settings.EXPORT_LIMIT
    )

    student_blog_field_names = ('type', 'student_number', 'sex', 'level', 'city', 'school')
    story_blog_field_names = ('source_type', 'author_name')

    @property
    def student_blog_fields(self):
        for field_name in self.fields:
            if field_name in self.student_blog_field_names:
                yield self[field_name]

    @property
    def story_blog_fields(self):
        for field_name in filter(lambda f: f in self.story_blog_field_names, self.fields):
            yield self[field_name]

    def clean(self):
        cleaned_data = super(SearchForm, self).clean()
        for k, v in cleaned_data.items():
            if isinstance(self.fields[k], forms.CharField):
                cleaned_data[k] = normalize(v) if v is not None else None
        return cleaned_data

    def clean_blog(self):
        blog_id = self.cleaned_data['blog']
        if blog_id:
            return get_object_or_404(Blog, id=int(blog_id))
        return None


class VocabularyForm(SearchForm):

    class Meta(SearchForm.Meta):
        help_texts = {
            'blog': _('The blog to search in'),
        }

    template_name = 'main/vocabulary/vocabulary_form.html'

    include_functional_words = forms.BooleanField(
        required=False, label=_('Include functional words'),
        help_text=_('Include the functional words in the search results.'),
        widget=widgets.CheckboxInput
    )

    contains = forms.CharField(
        max_length=100, required=False, label=_('Contains'), help_text=_('Enter a word or a part of it to search for.')
    )

    partial_contains = forms.BooleanField(
        required=False, label=_('Partial contains'), help_text=_('Search for a part of the word.'),
        widget=widgets.CheckboxInput, initial=True
    )

    not_contains = forms.CharField(
        max_length=100, required=False, label=_('Does not contain'),
        help_text=_('Enter a word part of it to exclude from the search results.')
    )

    partial_not_contains = forms.BooleanField(
        required=False, label=_('Partial does not contain'), help_text=_('Exclude a part of the word.'),
        widget=widgets.CheckboxInput, initial=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['blog'].required = True
        self.fields['blog'].empty_label = _('Select a blog')
        self.fields['blog'].widget.attrs.update({
            'class': 'custom-select',
            'title': self.fields['blog'].help_text,
        })
        self.fields['include_functional_words'].widget.attrs.update({
            'class': 'form-check-input',
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': self.fields['include_functional_words'].help_text,
        })
        self.fields['contains'].widget.attrs.update({
            'placeholder': self.fields['contains'].help_text,
            'class': 'form-control',
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': self.fields['contains'].help_text,
        })
        self.fields['partial_contains'].widget.attrs.update({
            'class': 'custom-control-input',
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': self.fields['partial_contains'].help_text,
        })
        self.fields['not_contains'].widget.attrs.update({
            'placeholder': self.fields['not_contains'].help_text,
            'class': 'form-control',
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': self.fields['not_contains'].help_text,
        })
        self.fields['partial_not_contains'].widget.attrs.update({
            'class': 'custom-control-input',
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': self.fields['partial_not_contains'].help_text,
        })
        del self.fields['search_query']


class NgramsForm(VocabularyForm):

    class Meta(VocabularyForm.Meta):
        pass

    template_name = 'main/ngrams/blog_ngrams_form.html'

    ngram_type = forms.ChoiceField(
        choices=[('bigram', _('Bigrams')), ('trigram', _('Trigrams'))], required=True, label=_('N-gram type'),
        help_text=_('Select the type of n-gram to search for.'), widget=widgets.RadioSelect, initial='bigram'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['include_functional_words']
        self.fields['ngram_type'].widget.attrs.update({
            'class': 'form-check-input',
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': self.fields['ngram_type'].help_text,
        })


class BlogComparisonForm(forms.Form):

    blogs = forms.ModelMultipleChoiceField(
        queryset=Blog.objects.all(), required=True, label=_('Blogs'),
        help_text=_('Select the blogs to compare.'),
        widget=widgets.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['blogs'].widget.attrs.update({
            'class': 'form-check-input',
            'title': self.fields['blogs'].help_text,
            'data-toggle': 'tooltip',
            'data-placement': 'top',
        })


class SurroundingWordsFrequencyForm(SearchForm):

    class Meta(SearchForm.Meta):
        pass

    template_name = 'main/surrounding/surrounding_words_frequency_form.html'

    position = forms.ChoiceField(
        choices=[('P', _('Previous words')), ('N', _('Next words'))], required=True, label=_('Position'),
        help_text=_('Select the position of the words to search for.'),
        widget=widgets.RadioSelect, initial='P'
    )

    partial_search = forms.BooleanField(
        required=False, label=_('Partial search'), help_text=_('Search for a part of the word.'),
        widget=widgets.CheckboxInput
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search_query'].help_text = _(
            'Enter a word or part of it to search for its previous and next words.'
        )
        self.fields['search_query'].widget.attrs.update({
            'placeholder': self.fields['search_query'].help_text,
            'title': self.fields['search_query'].help_text,
        })
        self.fields['position'].widget.attrs.update({
            'class': 'form-check-input',
            'title': self.fields['position'].help_text,
            'data-toggle': 'tooltip',
            'data-placement': 'top',
        })
        self.fields['partial_search'].widget.attrs.update({
            'class': 'custom-control-input',
            'title': self.fields['partial_search'].help_text,
            'data-toggle': 'tooltip',
            'data-placement': 'top',
        })


class WordDerivationsForm(SearchForm):

    class Meta(SearchForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search_query'].help_text = _(
            'Enter a word to search for its derivations (by adding the possible prefixes and suffixes).'
        )
        self.fields['search_query'].widget.attrs.update({
            'placeholder': self.fields['search_query'].help_text,
            'title': self.fields['search_query'].help_text,
        })
