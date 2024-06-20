# Generated by Django 5.0.6 on 2024-06-20 02:14

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
    ]

    operations = [
        migrations.RunPython(alter_site_name, reverse_code=migrations.RunPython.noop),
    ]
