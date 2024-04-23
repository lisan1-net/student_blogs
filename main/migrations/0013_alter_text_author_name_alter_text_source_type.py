# Generated by Django 5.0.3 on 2024-04-12 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_functionalword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='text',
            name='author_name',
            field=models.CharField(blank=True, help_text='Type of the text', max_length=100, null=True, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='text',
            name='source_type',
            field=models.CharField(blank=True, help_text='Source type', max_length=100, null=True, verbose_name='Source'),
        ),
    ]