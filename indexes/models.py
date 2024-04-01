from django.db import models
from django.utils.translation import gettext_lazy as _


class Word(models.Model):

    class Meta:
        verbose_name = _('Word')
        verbose_name_plural = _('Words')

    content = models.CharField(max_length=50, verbose_name=_('Word'), help_text=_('Word that is found in texts'))
    texts = models.ManyToManyField(
        'main.Text', verbose_name=_('Texts'), help_text=_('Texts that contain this word'), through='TextWord'
    )

    def __str__(self):
        return self.content


class TextWord(models.Model):

    class Meta:
        verbose_name = _('Text Word')
        verbose_name_plural = _('Text Words')

    text = models.ForeignKey(
        'main.Text', on_delete=models.CASCADE, verbose_name=_('Text'), help_text=_('Text that contains this word'),
        related_name='text_words'
    )
    word = models.ForeignKey(
        Word, on_delete=models.CASCADE, verbose_name=_('Word'), help_text=_('Word that is found in this text'),
        related_name='text_words'
    )
    frequency = models.PositiveIntegerField(
        verbose_name=_('Frequency'), help_text=_('Number of times this word appears in this text')
    )

    def __str__(self):
        return _('"%(word)s" in "%(text)s" [%(frequency)d]') % {
            'word': self.word, 'text': self.text, 'frequency': self.frequency
        }
