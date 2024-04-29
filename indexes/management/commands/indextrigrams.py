from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from indexes.models import Trigram
from main.models import Blog, Text


class Command(BaseCommand):

    help = _('Index trigrams from the indexed words of the blog texts')

    def add_arguments(self, parser):
        parser.add_argument('--blogs', nargs='+', type=int, help=_('Blog IDs to index words'))
        parser.add_argument('--clear', action='store_true', help=_('Clear all indexed words'))
        parser.add_argument('--max-texts', type=int, default=20, help=_('Maximum number of texts to index bigrams'))

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING(_('Clearing all indexed trigrams...')))
            Trigram.objects.all().delete()
            return
        if not options['blogs']:
            options['blogs'] = Blog.objects.values_list('id', flat=True)
        for blog_id in options['blogs']:
            if not Blog.objects.filter(id=blog_id).exists():
                raise CommandError(_('Blog with ID %(id)d does not exist') % {'id': blog_id})
        self.stdout.write(_('Number of texts that will be indexed: %(count)d') % {'count': options['max_texts']})
        texts = Text.objects.filter(blog__in=options['blogs'], trigrams_indexed=False)[:options['max_texts']]
        for text in texts:
            text_tokens = text.text_tokens.all().order_by('start')
            text.trigrams.all().delete()
            for word1, word2, word3 in zip(text_tokens, text_tokens[1:], text_tokens[2:]):
                try:
                    if word2.start - word1.end > 1 or word3.start - word2.end > 1:
                        continue
                    trigram, created = Trigram.objects.get_or_create(
                        first_token=word1.token, second_token=word2.token, third_token=word3.token,
                        text=text
                    )
                    trigram.frequency += 1
                    trigram.save()
                    self.stdout.write(_('Indexed %(trigram)s') % {'trigram': trigram})
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(_('Trigram "%(word1)s %(word2)s %(word3)s" already exists') % {
                        'word1': word1.token, 'word2': word2.token, 'word3': word3.token
                    }))
            text.trigrams_indexed = True
            text.save()
        self.stdout.write(self.style.SUCCESS(_('Finished indexing trigrams')))
