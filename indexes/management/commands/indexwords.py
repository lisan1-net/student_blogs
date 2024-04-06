from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from indexes.models import Token, TextToken
from indexes.utils import normalize, get_words_ranges
from main.models import Blog, Text


class Command(BaseCommand):

    help = _('Index words of the blog texts')

    def add_arguments(self, parser):
        parser.add_argument('--blogs', nargs='+', type=int, help=_('Blog IDs to index words'))
        parser.add_argument('--clear', action='store_true', help=_('Clear all indexed words'))
        parser.add_argument('--max-texts', type=int, default=20, help=_('Maximum number of texts to index words'))

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING(_('Clearing all indexed text words...')))
            Token.objects.all().delete()
            return
        if not options['blogs']:
            options['blogs'] = Blog.objects.values_list('id', flat=True)
        for blog_id in options['blogs']:
            if not Blog.objects.filter(id=blog_id).exists():
                raise CommandError(_('Blog with ID %(id)d does not exist') % {'id': blog_id})
        self.stdout.write(_('Number of texts that will be indexed: %(count)d') % {'count': options['max_texts']})
        texts = Text.objects.filter(blog__in=options['blogs'], words_indexed=False)[:options['max_texts']]
        for text in texts:
            self.stdout.write(_('Indexing words of "%(text)s"...') % {'text': text})
            last_index_position = text.index_progress
            self.stdout.write(_('Initial indexing progress: %(current)d/%(max)d' % {
                'current': last_index_position, 'max': text.max_index_progress
            }))
            for word_content, (start, end) in get_words_ranges(text.content):
                if end < last_index_position:
                    continue
                word_content = normalize(word_content)
                self.stdout.write(_('Indexing "%(token)s" [%(start)d:%(end)d]') % {
                    'token': word_content, 'start': start, 'end': end,
                })
                token, created = Token.objects.get_or_create(content=word_content)
                TextToken.objects.get_or_create(text=text, token=token, start=start, end=end)
            text.words_indexed = True
            text.save()
        self.stdout.write(self.style.SUCCESS(_('Finished indexing words')))
