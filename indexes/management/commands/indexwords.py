from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from indexes.models import Word, TextWord
from main.models import Blog
from main.utils import get_word_frequencies


class Command(BaseCommand):

    help = _('Index words of the blog texts')

    def add_arguments(self, parser):
        parser.add_argument('--blogs', nargs='+', type=int, help=_('Blog IDs to index words'))
        parser.add_argument('--clear', action='store_true', help=_('Clear all indexed words'))

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
        self.stdout.write(_('Indexing words...'))
        for blog_id in options['blogs']:
            blog = Blog.objects.get(id=blog_id)
            self.stdout.write(_('Indexing words of "%(blog)s"...') % {'blog': blog})
            for text in blog.text_set.all():
                if text.words_indexed:
                    continue
                self.stdout.write(_('Indexing words of "%(text)s"...') % {'text': text})
                frequencies = get_word_frequencies(text)
                for content, frequency in frequencies.items():
                    word, created = Word.objects.get_or_create(content=content)
                    text_word_query = TextWord.objects.filter(text=text, word=word)
                    if text_word_query.exists():
                        text_word = text_word_query.first()
                        text_word.frequency = frequency
                        text_word.save()
                    else:
                        TextWord.objects.create(text=text, word=word, frequency=frequency)
        self.stdout.write(self.style.SUCCESS(_('Finished indexing words')))
