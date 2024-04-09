from django.db import models
from django.utils.translation import gettext_lazy as _


class Token(models.Model):

    class Meta:
        verbose_name = _('Token')
        verbose_name_plural = _('Tokens')

    content = models.CharField(
        max_length=20, verbose_name=_('Content'), help_text=_('Content of the token'), unique=True
    )

    texts = models.ManyToManyField(
        'main.Text', verbose_name=_('Texts'), help_text=_('Texts that contain this token'), through='TextToken',
        related_name='tokens'
    )

    def __str__(self):
        return self.content


class TextToken(models.Model):

    class Meta:
        verbose_name = _('Text Token')
        verbose_name_plural = _('Text Tokens')
        unique_together = ('text', 'start', 'end')

    text = models.ForeignKey(
        'main.Text', on_delete=models.CASCADE, verbose_name=_('Text'), help_text=_('Text that contains this token'),
        related_name='text_tokens'
    )
    token = models.ForeignKey(
        Token, on_delete=models.CASCADE, verbose_name=_('Token'), help_text=_('Token that is found in this text'),
        related_name='text_tokens'
    )
    start = models.PositiveIntegerField(
        verbose_name=_('Start'), help_text=_('Start position of the token in the text')
    )
    end = models.PositiveIntegerField(
        verbose_name=_('End'), help_text=_('End position of the token in the text')
    )

    def __str__(self):
        return _('"%(token)s" in "%(text)s" [%(start)d:%(end)d]') % {
            'token': self.token, 'text': self.text, 'start': self.start, 'end': self.end
        }
