from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _, pgettext
from taggit.managers import TaggableManager

from main.utils import normalize
from indexes.models import TextWord


class Blog(models.Model):

    class Meta:
        verbose_name = _('Blog')
        verbose_name_plural = _('Blogs')

    title = models.CharField(max_length=100, verbose_name=_('Title'), help_text=_('Blog title'))
    description = models.TextField(blank=True, verbose_name=_('Description'), help_text=_('Blog description'))

    def __str__(self):
        return self.title

    def word_count(self):
        text_words = TextWord.objects.filter(text__blog=self, word__part='STEM')
        with_duplications = text_words.count()
        without_duplications = text_words.values('word').distinct().count()
        return with_duplications, without_duplications

    def get_word_count_display(self):
        with_duplications, without_duplications = self.word_count()
        return _('Words: %(words)d, Unique words: %(unique)d') % {
            'words': with_duplications, 'unique': without_duplications
        }


class Text(models.Model):

    TEXT_TYPE = [
        (None, ''),
        ('SPOKEN', _('Spoken')),
        ('WRITTEN', _('Written')),
        ('NOTEBOOKS', _('Notebooks')),
    ]

    SEX = [(None, ''), ('M', _('Male')), ('F', _('Female'))]

    class Meta:
        verbose_name = _('Text')
        verbose_name_plural = _('Texts')

    blog = models.ForeignKey(
        Blog, on_delete=models.CASCADE, verbose_name=_('Blog'), help_text=_('Blog that contains this text')
    )
    title = models.CharField(max_length=200, verbose_name=_('Title'), help_text=_('Title of the text'))
    content = models.TextField(verbose_name=_('Content'), help_text=_('Content of the text'))
    type = models.CharField(
        max_length=10, choices=TEXT_TYPE, verbose_name=_('Type'), help_text=_('Type of the text'), null=True, blank=True
    )
    student_number = models.IntegerField(
        verbose_name=_('Number'), help_text=_('Number of the student'), null=True, blank=True,
        validators=[validators.MinValueValidator(1)]
    )
    sex = models.CharField(
        max_length=1, choices=SEX, verbose_name=_('Sex'), help_text=_('Student sex'), null=True, blank=True
    )
    level = models.IntegerField(
        verbose_name=_('Level'), help_text=_('Level of the student'), null=True, blank=True,
        validators=[validators.MinValueValidator(1)]
    )
    school = models.CharField(
        max_length=100, verbose_name=_('School'), help_text=_('School of the student'), null=True, blank=True
    )
    city = models.CharField(
        max_length=100, verbose_name=_('City'), help_text=_('City of the student'), null=True, blank=True
    )
    author_name = models.CharField(
        max_length=100, verbose_name=_('Author name'), help_text=_('Author name'), null=True, blank=True,
    )
    source_type = models.CharField(
        max_length=100, verbose_name=_('Source type'), help_text=_('Source type'), null=True, blank=True,
    )
    added = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Added on'), help_text=_('Date and time of adding the text to the database')
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name=_('Last updated on'),
        help_text=_('Date and time of the last update of the text in the database')
    )
    tags = TaggableManager(blank=True)
    words_indexed = models.BooleanField(
        default=False, verbose_name=_('Words indexed'), editable=False,
        help_text=_('Indicates whether the words of this text are indexed or not')
    )

    def __str__(self):
        return self.title

    @property
    def title_normalized(self):
        return normalize(self.title)

    @property
    def content_normalized(self):
        return normalize(self.content)

    def get_student_number_display(self):
        translation = _('Student number %(number)d')
        if self.sex == 'M':
            translation = pgettext('Male', 'Student number %(number)d')
        elif self.sex == 'F':
            translation = pgettext('Female', 'Student number %(number)d')
        return translation % {'number': self.student_number}

    def get_level_display(self):
        return _('Level %(level)d') % {'level': self.level}
