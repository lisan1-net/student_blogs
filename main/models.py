from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class Blog(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Author(models.Model):
    name = models.CharField(max_length=150)
    sex = models.CharField(max_length=1, choices=[('M', _('Male')), ('F', _('Female'))])
    area = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class Text(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    grade = models.CharField(max_length=50, null=True, blank=True)
    part = models.CharField(max_length=100, null=True, blank=True)
    editor = models.CharField(max_length=100, null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    def __str__(self):
        return self.title
