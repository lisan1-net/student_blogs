from django.apps import apps
from django.core.management import BaseCommand
from django.db import reset_queries
from django.db.utils import IntegrityError


class Command(BaseCommand):

    help = 'Migrate TextWords to TextTokens and Words to Tokens'

    def add_arguments(self, parser):
        parser.add_argument('--max-instances', type=int, default=0, help='Maximum number of instances to migrate')

    def handle(self, *args, **options):
        TextWord = apps.get_model('indexes', 'TextWord')
        Token = apps.get_model('indexes', 'Token')
        TextToken = apps.get_model('indexes', 'TextToken')
        start = 0
        end = 0
        token_content = ''
        token_index = 1
        text_words = TextWord.objects.exclude(
            text__in=TextToken.objects.values('text'), start__in=TextToken.objects.values('start'),
            end__in=TextToken.objects.values('end')
        )
        if options['max_instances']:
            text_words = text_words[:options['max_instances']]
        self.stdout.write('Number of text words to migrate: %d' % text_words.count())
        text_word = None
        for word_index, text_word in enumerate(text_words.iterator(), 1):  # Use iterator to fetch objects in chunks
            self.stdout.write('Migrating text word %d: %s' % (word_index, str(text_word)))
            if text_word.start == start and text_word.end == end:
                token_content += text_word.word.content
            elif token_content:
                try:
                    token, created = Token.objects.get_or_create(content=token_content)
                    text_token, created = TextToken.objects.get_or_create(text=text_word.text, token=token, start=start, end=end)
                    self.stdout.write('Migrated text token %d: %s' % (token_index, str(text_token)))
                except IntegrityError:
                    self.stdout.write(self.style.ERROR('Failed to migrate text token %d: %s' % (token_index, token_content)))
                token_index += 1
                token_content = text_word.word.content
            start = text_word.start
            end = text_word.end
            if word_index % 5000 == 0:  # Clear the QuerySet cache every 5000 iterations
                reset_queries()
        if token_content and text_word:
            try:
                token, created = Token.objects.get_or_create(content=token_content)
                text_token, created = TextToken.objects.get_or_create(text=text_word.text, token=token, start=start, end=end)
                self.stdout.write('Migrated text token %d: %s' % (token_index, str(text_token)))
            except IntegrityError:
                self.stdout.write(self.style.ERROR('Failed to migrate text token %d: %s' % (token_index, token_content)))
        self.stdout.write(self.style.SUCCESS('Finished migrating text tokens'))