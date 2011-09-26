# -*- coding: utf-8 -*-
# (c) 2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

class Entry(models.Model):
    """
    Definition of entries.
    """
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    slug = models.SlugField(max_length=80)
    content = models.TextField(verbose_name=_(u'Content'), null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_(u'Is active'))
    allow_comments = models.BooleanField(verbose_name=_(u'Allow comments'))
    registered = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Entry')
        verbose_name_plural = _(u'Entries')
        ordering = ('registered',)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:entry', args=[self.slug])

