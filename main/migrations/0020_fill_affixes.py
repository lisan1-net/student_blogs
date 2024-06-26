# Generated by Django 5.0.4 on 2024-05-22 10:52

from django.db import migrations

conjunctions = ('و', 'ف')
name_prefixes = ('ال', 'لل', 'كال', 'ب', 'ك', 'ل')
verb_prefixes = ('ي', 'ن', 'ت', 'أ', 'است', 'ا', 'إ')
extra_prefixes = ('ل', 'س')

conjunction_name_prefixes = [
    f'{conjunction}{name_prefix}' for conjunction in conjunctions for name_prefix in name_prefixes
]
conjunction_verb_prefixes = [
    f'{conjunction}{verb_prefix}' for conjunction in conjunctions for verb_prefix in verb_prefixes
]
extra_verb_prefixes = [
    f'{extra_prefix}{verb_prefix}' for extra_prefix in extra_prefixes for verb_prefix in verb_prefixes
]


def fill_prefixes(apps, schema_editor):
    Prefix = apps.get_model('main', 'Prefix')
    prefixes = []
    for prefix in [*name_prefixes, *verb_prefixes, *conjunctions]:
        prefixes.append(Prefix(content=prefix))
    for conjunction_name_prefix in conjunction_name_prefixes:
        prefixes.append(Prefix(content=conjunction_name_prefix))
    for conjunction_verb_prefix in conjunction_verb_prefixes:
        prefixes.append(Prefix(content=conjunction_verb_prefix))
    for future_verb_prefix in extra_verb_prefixes:
        prefixes.append(Prefix(content=future_verb_prefix))
    Prefix.objects.bulk_create(prefixes)


we_suffix = 'نا'
common_suffixes = ('ين', 'ون', 'ان')
possession_suffixes = ('ه', 'ي', 'ها', 'هما', 'هم', 'هن', 'كما', 'كم', 'كن')
name_suffixes = ('ك', 'ات', 'ة')
verb_suffixes_middle = ('ن', 'ت', 'ا')
verb_suffixes_final = ('وا', 'وه', 'تما', 'تم')

middle_possession_suffixes = [
    f'{middle}{possession}' for middle in verb_suffixes_middle for possession in possession_suffixes
]
middle_common_suffixes = [f'{middle}{common}' for middle in verb_suffixes_middle for common in common_suffixes]


def fill_suffixes(apps, schema_editor):
    Suffix = apps.get_model('main', 'Suffix')
    suffixes = []
    for suffix in [
        *common_suffixes, *name_suffixes, *verb_suffixes_middle, *verb_suffixes_final, *possession_suffixes, we_suffix
    ]:
        suffixes.append(Suffix(content=suffix))
    for middle_possession in middle_possession_suffixes:
        suffixes.append(Suffix(content=middle_possession))
    for middle_common in middle_common_suffixes:
        suffixes.append(Suffix(content=middle_common))
    Suffix.objects.bulk_create(suffixes)


def fill_compatibilities(apps, schema_editor):
    Prefix = apps.get_model('main', 'Prefix')
    Suffix = apps.get_model('main', 'Suffix')
    for prefix in Prefix.objects.filter(content__in=conjunctions):
        prefix.suffixes.add(*Suffix.objects.all())
    for prefix in Prefix.objects.filter(content__in=(*name_prefixes, *conjunction_name_prefixes)):
        prefix.suffixes.add(
            *Suffix.objects.filter(content__in=(*common_suffixes, *possession_suffixes, *name_suffixes))
        )
    for prefix in Prefix.objects.filter(
            content__in=(*verb_prefixes, *conjunction_verb_prefixes, *extra_verb_prefixes)
    ):
        prefix.suffixes.add(
            *Suffix.objects.filter(
                content__in=(
                    *common_suffixes, *possession_suffixes, *verb_suffixes_middle, *verb_suffixes_final, we_suffix,
                    *middle_common_suffixes, *middle_possession_suffixes
                )
            )
        )


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_suffix_prefix'),
    ]

    operations = [
        migrations.RunPython(
            fill_prefixes,
            reverse_code=lambda apps, schema_editor: apps.get_model('main', 'Prefix').objects.all().delete()
        ),
        migrations.RunPython(
            fill_suffixes,
            reverse_code=lambda apps, schema_editor: apps.get_model('main', 'Suffix').objects.all().delete()
        ),
        migrations.RunPython(fill_compatibilities, reverse_code=migrations.RunPython.noop),
    ]
