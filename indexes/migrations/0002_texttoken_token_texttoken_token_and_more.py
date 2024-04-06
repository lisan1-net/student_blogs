# Generated by Django 5.0.3 on 2024-04-06 06:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexes', '0001_initial'),
        ('main', '0011_alter_text_sex_alter_text_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.PositiveIntegerField(help_text='Start position of the token in the text', verbose_name='Start')),
                ('end', models.PositiveIntegerField(help_text='End position of the token in the text', verbose_name='End')),
                ('text', models.ForeignKey(help_text='Text that contains this token', on_delete=django.db.models.deletion.CASCADE, related_name='text_tokens', to='main.text', verbose_name='Text')),
            ],
            options={
                'verbose_name': 'Text Token',
                'verbose_name_plural': 'Text Tokens',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(help_text='Content of the token', max_length=20, unique=True, verbose_name='Content')),
                ('texts', models.ManyToManyField(help_text='Texts that contain this token', related_name='tokens', through='indexes.TextToken', to='main.text', verbose_name='Texts')),
            ],
            options={
                'verbose_name': 'Token',
                'verbose_name_plural': 'Tokens',
            },
        ),
        migrations.AddField(
            model_name='texttoken',
            name='token',
            field=models.ForeignKey(help_text='Token that is found in this text', on_delete=django.db.models.deletion.CASCADE, related_name='text_tokens', to='indexes.token', verbose_name='Token'),
        ),
        migrations.AlterUniqueTogether(
            name='texttoken',
            unique_together={('text', 'token', 'start', 'end')},
        ),
    ]
