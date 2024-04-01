# Generated by Django 5.0.3 on 2024-04-01 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_text_words_indexed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='text',
            name='sex',
            field=models.CharField(blank=True, choices=[(None, ''), ('M', 'Male'), ('F', 'Female')], help_text='Student sex', max_length=1, null=True, verbose_name='Sex'),
        ),
        migrations.AlterField(
            model_name='text',
            name='type',
            field=models.CharField(blank=True, choices=[(None, ''), ('SPOKEN', 'Spoken'), ('WRITTEN', 'Written'), ('NOTEBOOKS', 'Notebooks')], help_text='Type of the text', max_length=10, null=True, verbose_name='Type'),
        ),
    ]
