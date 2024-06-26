# Generated by Django 5.0.3 on 2024-03-30 13:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_text_city_alter_text_level_alter_text_school_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='text',
            name='student_number',
            field=models.IntegerField(blank=True, help_text='Number of the student', null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Number'),
        ),
    ]
