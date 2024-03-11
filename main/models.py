from functools import cached_property
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from pyarabic.araby import strip_tashkeel, strip_tatweel


class Blog(models.Model):

    class Meta:
        verbose_name = _('Blog')
        verbose_name_plural = _('Blogs')

    title = models.CharField(max_length=100, verbose_name=_('Title'), help_text=_('Blog title'))
    description = models.TextField(blank=True, verbose_name=_('Description'), help_text=_('Blog description'))

    def __str__(self):
        return self.title


class Author(models.Model):

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    name = models.CharField(max_length=150, verbose_name=_('Name'), help_text=_('Author name'))
    sex = models.CharField(
        max_length=1, choices=[('M', _('Male')), ('F', _('Female'))], verbose_name=_('Sex'), help_text=_('Author sex')
    )
    area = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Area'), help_text=_('Author area'))
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('City'), help_text=_('Author city'))

    def __str__(self):
        return self.name


class Text(models.Model):

    class Meta:
        verbose_name = _('Text')
        verbose_name_plural = _('Texts')

    blog = models.ForeignKey(
        Blog, on_delete=models.CASCADE, verbose_name=_('Blog'), help_text=_('Blog where this text is in')
    )
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, verbose_name=_('Author'), help_text=_('Author that wrote this article')
    )
    title = models.CharField(max_length=200, verbose_name=_('Title'), help_text=_('Title of the text'))
    content = models.TextField(verbose_name=_('Content'), help_text=_('Content of the text'))
    source = models.CharField(
        max_length=200, null=True, blank=True, verbose_name=_('Source'), help_text=_('The source document of the text')
    )
    grade = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_('Grade'),
        help_text=_('Grade of the student studying this text')
    )
    part = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_('Part'),
        help_text=_('Part of the book containing this text')
    )
    editor = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_('Editor'),
        help_text=_('Editor of the book containing this text')
    )
    added = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Added on'), help_text=_('Date and time of adding the text to the database')
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name=_('Last updated on'),
        help_text=_('Date and time of the last update of the text in the database')
    )
    tags = TaggableManager()

    def __str__(self):
        return self.title

    @cached_property
    def title_normalized(self):
        return strip_tashkeel(strip_tatweel(self.title)).lower()

    @cached_property
    def content_normalized(self):
        return strip_tashkeel(strip_tatweel(self.content)).lower()
