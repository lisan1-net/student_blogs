# Generated by Django 5.0.4 on 2024-04-29 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_text_bigrams_indexed'),
    ]

    operations = [
        migrations.AddField(
            model_name='text',
            name='trigrams_indexed',
            field=models.BooleanField(default=False, editable=False, help_text='Indicates whether the trigrams of this text are indexed or not', verbose_name='Trigrams indexed'),
        ),
    ]
