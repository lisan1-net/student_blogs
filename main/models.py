from django.conf import settings
from django.core import validators
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, pgettext
from taggit.managers import TaggableManager

from indexes.models import TextToken, Bigram, Trigram


class Blog(models.Model):

    class Meta:
        verbose_name = _('Blog')
        verbose_name_plural = _('Blogs')

    title = models.CharField(max_length=100, verbose_name=_('Title'), help_text=_('Blog title'))

    description = models.TextField(blank=True, verbose_name=_('Description'), help_text=_('Blog description'))

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Owner'), help_text=_('Owner of the blog'),
        db_default=1
    )

    public = models.BooleanField(
        db_default=True, verbose_name=_('Public'), help_text=_('Indicates whether the blog is public or not')
    )

    def __str__(self):
        return self.title

    def word_count(self):
        text_words = TextToken.objects.filter(text__blog=self)
        with_duplications = text_words.count()
        without_duplications = text_words.values('token').distinct().count()
        return with_duplications, without_duplications

    def get_word_count_display(self):
        with_duplications, without_duplications = self.word_count()
        return _('Words: %(words)d, Unique words: %(unique)d') % {
            'words': with_duplications, 'unique': without_duplications
        }

    def text_count(self):
        return self.text_set.count()

    def school_count(self):
        return self.text_set.values('school').exclude(school__isnull=True).distinct().count()

    def student_count_per_level(self):
        return self.text_set.values('level').exclude(level__isnull=True).annotate(
            student_count=models.Count('student_number')
        ).order_by('level').values_list('level', 'student_count')

    def most_frequent_words(self, limit=10):
        return TextToken.objects.filter(text__blog=self).exclude(
            token__content__in=FunctionalWord.objects.values_list('content', flat=True)).values('token').annotate(
            count=models.Count('token')
        ).order_by('-count')[:limit].values_list('token__content', 'count')

    def is_word_fully_indexed(self):
        return not self.text_set.filter(words_indexed=False).exists()

    def is_bigram_fully_indexed(self):
        return not self.text_set.filter(bigrams_indexed=False).exists()

    def is_trigram_fully_indexed(self):
        return not self.text_set.filter(trigrams_indexed=False).exists()

    def most_frequent_bigrams(self, count=100):
        return Bigram.objects.filter(text__blog=self).prefetch_related(
            'first_token', 'second_token'
        ).values('first_token__content', 'second_token__content').annotate(
            frequency=Sum('frequency')
        ).order_by('-frequency')[:count].values_list('first_token__content', 'second_token__content', 'frequency')

    def most_frequent_trigrams(self, count=100):
        return Trigram.objects.filter(text__blog=self).prefetch_related(
            'first_token', 'second_token', 'third_token'
        ).values('first_token__content', 'second_token__content', 'third_token__content').annotate(
            frequency=Sum('frequency')
        ).order_by('-frequency')[:count].values_list(
            'first_token__content', 'second_token__content', 'third_token__content', 'frequency'
        )

    @property
    def most_frequent_words_extended(self):
        return self.most_frequent_words(200)


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
    author_name = models.CharField(  # Has been changed to type.
        max_length=100, verbose_name=_('Type'), help_text=_('Type of the text'), null=True, blank=True,
    )
    source_type = models.CharField(  # Has been changed to source.
        max_length=100, verbose_name=_('Source'), help_text=_('Source type'), null=True, blank=True,
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
    bigrams_indexed = models.BooleanField(
        default=False, verbose_name=_('Bigrams indexed'), editable=False,
        help_text=_('Indicates whether the bigrams of this text are indexed or not')
    )
    trigrams_indexed = models.BooleanField(
        default=False, verbose_name=_('Trigrams indexed'), editable=False,
        help_text=_('Indicates whether the trigrams of this text are indexed or not')
    )

    def __str__(self):
        return self.title

    @property
    def word_index_progress(self):
        return TextToken.objects.filter(text=self).aggregate(models.Max('end')).get('end__max') or 0

    @property
    def word_max_index_progress(self):
        return len(self.content)

    def get_student_number_display(self):
        translation = _('Student number %(number)d')
        if self.sex == 'M':
            translation = pgettext('Male', 'Student number %(number)d')
        elif self.sex == 'F':
            translation = pgettext('Female', 'Student number %(number)d')
        return translation % {'number': self.student_number}

    def get_level_display(self):
        return _('Level %(level)d') % {'level': self.level}


class FunctionalWord(models.Model):

    class Meta:
        verbose_name = _('Functional Word')
        verbose_name_plural = _('Functional Words')

    content = models.CharField(
        max_length=10, verbose_name=_('Content'), help_text=_('Content of the functional word'), unique=True
    )

    def __str__(self):
        return self.content


class Announcement(models.Model):

    class Meta:
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        ordering = ('-posted_on',)

    title = models.CharField(max_length=200, verbose_name=_('Title'), help_text=_('Title of the announcement'))
    description = models.TextField(
        verbose_name=_('Description'), help_text=_('Description of the announcement'), null=True, blank=True
    )
    image_link = models.URLField(
        verbose_name=_('Image link'), help_text=_('Link to the image of the announcement'), null=True, blank=True
    )
    link = models.URLField(
        verbose_name=_('Link'), help_text=_('Link to the announcement'), null=True, blank=True
    )
    posted_on = models.DateTimeField(
        verbose_name=_('Added on'), help_text=_('Date and time of adding the announcement'),
        default=timezone.now
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_('Active'), help_text=_('Indicates whether the announcement is shown or not')
    )

    def __str__(self):
        return self.title


class DictionaryDefinition(models.Model):

    class Meta:
        verbose_name = _('Dictionary Definition')
        verbose_name_plural = _('Dictionary Definitions')

    term = models.CharField(max_length=50, verbose_name=_('Term'), help_text=_('Term in the dictionary'))
    definition = models.TextField(verbose_name=_('Definition'), help_text=_('Definition of the term'))

    def __str__(self):
        return self.term


class Prefix(models.Model):

    class Meta:
        verbose_name = _('Prefix')
        verbose_name_plural = _('Prefixes')

    content = models.CharField(
        max_length=10, verbose_name=_('Content'), help_text=_('Content of the prefix'), unique=True
    )

    suffixes = models.ManyToManyField(
        'Suffix', related_name='prefixes', verbose_name=_('Compatible with suffixes')
    )

    def __str__(self):
        return self.content


class Suffix(models.Model):
    class Meta:
        verbose_name = _('Suffix')
        verbose_name_plural = _('Suffixes')

    content = models.CharField(
        max_length=10, verbose_name=_('Content'), help_text=_('Content of the suffix'), unique=True
    )

    def __str__(self):
        return self.content
