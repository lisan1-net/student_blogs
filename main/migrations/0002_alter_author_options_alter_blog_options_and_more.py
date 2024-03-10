# Generated by Django 5.0.2 on 2024-03-05 14:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='author',
            options={'verbose_name': 'Author', 'verbose_name_plural': 'Authors'},
        ),
        migrations.AlterModelOptions(
            name='blog',
            options={'verbose_name': 'Blog', 'verbose_name_plural': 'Blogs'},
        ),
        migrations.AlterModelOptions(
            name='text',
            options={'verbose_name': 'Text', 'verbose_name_plural': 'Texts'},
        ),
        migrations.AddField(
            model_name='text',
            name='source',
            field=models.CharField(blank=True, help_text='The source document of the text', max_length=200, null=True, verbose_name='Source'),
        ),
        migrations.AlterField(
            model_name='author',
            name='area',
            field=models.CharField(blank=True, help_text='Author area', max_length=100, null=True, verbose_name='Area'),
        ),
        migrations.AlterField(
            model_name='author',
            name='city',
            field=models.CharField(blank=True, help_text='Author city', max_length=100, null=True, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='author',
            name='name',
            field=models.CharField(help_text='Author name', max_length=150, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='author',
            name='sex',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], help_text='Author sex', max_length=1, verbose_name='Sex'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='description',
            field=models.TextField(blank=True, help_text='Blog description', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='title',
            field=models.CharField(help_text='Blog title', max_length=100, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='text',
            name='added',
            field=models.DateTimeField(auto_now_add=True, help_text='Date and time of adding the text to the database', verbose_name='Added on'),
        ),
        migrations.AlterField(
            model_name='text',
            name='author',
            field=models.ForeignKey(help_text='Author that wrote this article', on_delete=django.db.models.deletion.CASCADE, to='main.author', verbose_name='Author'),
        ),
        migrations.AlterField(
            model_name='text',
            name='blog',
            field=models.ForeignKey(help_text='Blog where this text is in', on_delete=django.db.models.deletion.CASCADE, to='main.blog', verbose_name='Blog'),
        ),
        migrations.AlterField(
            model_name='text',
            name='content',
            field=models.TextField(help_text='Content of the text', verbose_name='Content'),
        ),
        migrations.AlterField(
            model_name='text',
            name='editor',
            field=models.CharField(blank=True, help_text='Editor of the book containing this text', max_length=100, null=True, verbose_name='Editor'),
        ),
        migrations.AlterField(
            model_name='text',
            name='grade',
            field=models.CharField(blank=True, help_text='Grade of the student studying this text', max_length=50, null=True, verbose_name='Grade'),
        ),
        migrations.AlterField(
            model_name='text',
            name='part',
            field=models.CharField(blank=True, help_text='Part of the book containing this text', max_length=100, null=True, verbose_name='Part'),
        ),
        migrations.AlterField(
            model_name='text',
            name='title',
            field=models.CharField(help_text='Title of the text', max_length=200, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='text',
            name='updated',
            field=models.DateTimeField(auto_now=True, help_text='Date and time of the last update of the text in the database', verbose_name='Last updated on'),
        ),
    ]