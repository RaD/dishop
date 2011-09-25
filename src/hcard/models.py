# -*- coding: utf-8 -*-
# (c) 2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.db import models
from django.utils.translation import ugettext_lazy as _

class Address(models.Model):
    postal_code = models.CharField(verbose_name=_(u'Postal Code'), max_length=6, blank=True, null=True)
    country_name = models.CharField(verbose_name=_(u'Country Name'), max_length=120)
    region = models.CharField(verbose_name=_(u'Region'), max_length=80, blank=True, null=True)
    locality = models.CharField(verbose_name=_(u'Locality'), max_length=80)
    street_address = models.CharField(verbose_name=_(u'Street Address'), max_length=255)
    extended_address = models.CharField(verbose_name=_(u'Extended Address'), max_length=255, blank=True, null=True)
    post_office_box = models.CharField(verbose_name=_(u'Post Office Box'), max_length=32, blank=True, null=True)

    class Meta:
        verbose_name = _(u'Address')
        verbose_name_plural = _(u'Addresses')
        ordering = ('country_name', 'locality', 'street_address',)

    def __unicode__(self):
        return _(u'%(street)s, %(locality)s, %(country)s') % {
            'street': self.street_address,
            'locality': self.locality,
            'country': self.country_name,
            }
