# Generated by Django 5.0.6 on 2024-06-30 14:30
from django.conf import settings
from django.db import migrations
from django.utils.translation import gettext_lazy as _


def alter_site_name(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    default_site = Site.objects.get(pk=settings.SITE_ID)
    default_site.name = _('Students blog')
    default_site.domain = 'corpus.lisan1.com'
    default_site.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_alter_blog_owner'),
        ('sites', '0002_alter_domain_unique')
    ]

    operations = [
        migrations.RunPython(alter_site_name, reverse_code=migrations.RunPython.noop),
    ]
