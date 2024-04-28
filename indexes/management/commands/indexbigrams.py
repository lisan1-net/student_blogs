from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from indexes.models import Bigram
from main.models import Blog, Text


class Command(BaseCommand):

    help = _('Index bigrams from the indexed words of the blog texts')

    def add_arguments(self, parser):
        parser.add_argument('--blogs', nargs='+', type=int, help=_('Blog IDs to index words'))
        parser.add_argument('--clear', action='store_true', help=_('Clear all indexed words'))
        parser.add_argument('--max-texts', type=int, default=20, help=_('Maximum number of texts to index bigrams'))

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING(_('Clearing all indexed bigrams...')))
            Bigram.objects.all().delete()
            return
        if not options['blogs']:
            options['blogs'] = Blog.objects.values_list('id', flat=True)
        for blog_id in options['blogs']:
            if not Blog.objects.filter(id=blog_id).exists():
                raise CommandError(_('Blog with ID %(id)d does not exist') % {'id': blog_id})
        self.stdout.write(_('Number of texts that will be indexed: %(count)d') % {'count': options['max_texts']})
        texts = Text.objects.filter(blog__in=options['blogs'], bigrams_indexed=False)[:options['max_texts']]
        for text in texts:
            self.stdout.write(_('Indexing bigrams of "%(text)s"...') % {'text': text})
            last_index_position = text.bigram_index_progress
            self.stdout.write(_('Initial indexing progress: %(current)d/%(max)d' % {
                'current': last_index_position, 'max': text.bigram_max_index_progress
            }))
            text_tokens = text.text_tokens.all()
            for word1, word2 in zip(text_tokens, text_tokens[1:]):
                if word2.start < last_index_position:
                    continue
                try:
                    bigram, created = Bigram.objects.get_or_create(first_text_token=word1, second_text_token=word2)
                    self.stdout.write(_('Indexed "%(bigram)s"') % {'bigram': bigram})
                except IntegrityError:
                    pass
            text.bigrams_indexed = True
            text.save()
        self.stdout.write(self.style.SUCCESS(_('Finished indexing bigrams')))
