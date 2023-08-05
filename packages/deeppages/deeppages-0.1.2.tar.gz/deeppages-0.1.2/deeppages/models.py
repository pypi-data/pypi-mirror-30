from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.urls import resolve, reverse, Resolver404


class Page(models.Model):
    ''' The unique model for Deep Pages '''

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=_('This name will be used to identify the page. Ex.: my '
                    'page name'))

    path = models.CharField(
        max_length=100,
        help_text=_('Type the absolute path. Ex.: /my-page-name/'))

    title = models.CharField(
        max_length=100,
        default=None,
        blank=True,
        null=True)

    content = models.TextField(null=True, blank=True, default=None)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    changed_at = models.DateTimeField('Changed At', auto_now=True)

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
        ordering = ('name',)
        get_latest_by = 'changed_at'

    def _validate_path(self):
        try:
            resolve(self.path)

        except Resolver404:
            return True

        else:
            return self.path != reverse('deeppages:__deep_page_view__')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def render(self, context=None, callback=None):
        from .utils import render_content
        ctx = context or {}
        return render_content(self.content, ctx)

    def save(self, *args, **kwargs):
        if not self._validate_path():
            print(_('This PATH is already being used. Try a different path.'))
            return False
        else:
            return super(Page, self).save(*args, **kwargs)
