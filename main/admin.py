from django.apps import apps
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _

from main.models import Blog, Text

ModelAdmin.list_per_page = 50

app = apps.get_app_config('main')
admin.site.site_header = app.verbose_name
admin.site.site_title = app.verbose_name
admin.site.empty_value_display = _('Unspecified')


@admin.register(Blog)
class BlogAdmin(ModelAdmin):

    list_display = ('title', 'description')
    search_fields = ('title', 'description')


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):

    list_display = (
        'title', 'type', 'student_number', 'sex', 'level', 'school', 'city', 'author_name', 'source_type',
    )
    list_filter = tuple(e for e in list_display if e not in ('author_name', 'title'))
    search_fields = ('title', 'content', 'school', 'city', 'author_name')
