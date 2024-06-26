# Generated by Django 5.0.4 on 2024-05-22 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_text_trigrams_indexed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Suffix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(help_text='Content of the suffix', max_length=10, unique=True, verbose_name='Content')),
            ],
            options={
                'verbose_name': 'Suffix',
                'verbose_name_plural': 'Suffixes',
            },
        ),
        migrations.CreateModel(
            name='Prefix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(help_text='Content of the prefix', max_length=10, unique=True, verbose_name='Content')),
                ('suffixes', models.ManyToManyField(related_name='prefixes', to='main.suffix', verbose_name='Compatible with suffixes')),
            ],
            options={
                'verbose_name': 'Prefix',
                'verbose_name_plural': 'Prefixes',
            },
        ),
    ]
