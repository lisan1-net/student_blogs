from django.apps import apps
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.forms import CheckboxSelectMultiple
from django.utils.translation import gettext_lazy as _, ngettext
from guardian.admin import GuardedModelAdmin

from main.models import *

ModelAdmin.list_per_page = 50

app = apps.get_app_config('main')
admin.site.site_header = app.verbose_name
admin.site.site_title = app.verbose_name
admin.site.empty_value_display = _('Unspecified')


@admin.register(Blog)
class BlogAdmin(GuardedModelAdmin):

    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    user_owned_objects_field = 'owner'
    user_can_access_owned_objects_only = True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(Text)
class TextAdmin(GuardedModelAdmin):

    list_display = (
        'title', 'type', 'student_number', 'sex', 'level', 'school', 'city', 'author_name', 'source_type',
    )
    list_filter = tuple(e for e in list_display if e not in ('title', )) + ('blog', 'tags')
    search_fields = ('title', 'content', 'school', 'city')
    user_owned_objects_field = 'blog__owner'
    user_can_access_owned_objects_only = True

    def move_to_blog(self, request, queryset, blog_id):
        blog = Blog.objects.get(pk=blog_id)
        updated = queryset.update(blog_id=blog_id)
        self.message_user(
            request,
            ngettext(
                '%(count)d text moved to "%(blog)s".',
                '%(count)d texts moved to "%(blog)s".',
                updated,
            ) % {'count': updated, 'blog': blog.title},
            messages.SUCCESS,
        )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if self.has_change_permission(request):
            for blog in Blog.objects.all():
                if not request.user.has_perm('change_blog', blog):
                    continue
                blog_id = blog.pk
                blog_title = blog.title
                action_name = f'move_to_blog_{blog_id}'
                if action_name not in actions:
                    def move_to_blog(model_admin, request, queryset, blog_id=blog_id):
                        model_admin.move_to_blog(request, queryset, blog_id)

                    actions[action_name] = (
                        move_to_blog,
                        action_name,
                        _('Move to "%s"') % blog_title
                    )
        return actions

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'blog':
            kwargs['queryset'] = Blog.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(FunctionalWord)
class FunctionalWordAdmin(admin.ModelAdmin):

    search_fields = ('content',)
    list_display = ('content',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    search_fields = ('title', 'description')
    list_display = ('title', 'link', 'posted_on', 'is_active')
    list_filter = ('is_active', 'posted_on')


@admin.register(DictionaryDefinition)
class DictionaryDefinitionAdmin(admin.ModelAdmin):

    search_fields = ('term', 'definition')
    list_display = search_fields


@admin.register(Prefix)
class PrefixAdmin(admin.ModelAdmin):
    list_display = ['content']
    search_fields = ['content']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs['widget'] = CheckboxSelectMultiple
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Suffix)
class SuffixAdmin(admin.ModelAdmin):
    list_display = ['content']
    search_fields = ['content']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs['widget'] = CheckboxSelectMultiple
        return super().formfield_for_manytomany(db_field, request, **kwargs)
