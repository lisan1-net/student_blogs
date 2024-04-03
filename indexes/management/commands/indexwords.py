from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from indexes.models import Word, TextWord
from main.models import Blog, Text
from indexes.utils import *


class Command(BaseCommand):

    help = _('Index words of the blog texts')

    def add_arguments(self, parser):
        parser.add_argument('--blogs', nargs='+', type=int, help=_('Blog IDs to index words'))
        parser.add_argument('--clear', action='store_true', help=_('Clear all indexed words'))
        parser.add_argument('--max-texts', type=int, default=20, help=_('Maximum number of texts to index words'))

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING(_('Clearing all indexed text words...')))
            Word.objects.all().delete()
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
            for word_content, (start, end) in get_words_ranges(text.content):
                for t, w in zip(['PREFIX', 'STEM', 'SUFFIX'], segment(word_content)):
                    if w == '':
                        continue
                    part = ''
                    match t:
                        case 'PREFIX':
                            part = _('Prefix')
                        case 'STEM':
                            part = _('Stem')
                        case 'SUFFIX':
                            part = _('Suffix')
                    self.stdout.write(_('Indexing %(part)s "%(word)s" [%(start)d:%(end)d]') % {
                        'word': w, 'start': start, 'end': end, 'part': part
                    })
                    word, created = Word.objects.get_or_create(content=w, part=t)
                    TextWord.objects.update_or_create(text=text, word=word, start=start, end=end)
            text.words_indexed = True
            text.save()
        self.stdout.write(self.style.SUCCESS(_('Finished indexing words')))
