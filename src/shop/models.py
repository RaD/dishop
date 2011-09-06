# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.db import models
from django.contrib.admin.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape

from datetime import datetime

from sorl.thumbnail.shortcuts import get_thumbnail
from tagging.fields import TagField
from tagging.utils import parse_tag_input

class Category(models.Model):
    """
    Definition of categories. May link on itself to make some kind of hierarchy.
    """
    parent = models.ForeignKey(u'self', verbose_name=_(u'Parent'), blank=True, null=True)
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    slug = models.SlugField(max_length=80)

    class Meta:
        verbose_name = _(u'Category')
        verbose_name_plural = _(u'Categories')
        ordering = ('title',)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return u'/category/%s/' % self.slug

class Color(models.Model):
    """
    Definition of item's colors.
    """
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    slug = models.SlugField(max_length=80)
    color = models.CharField(verbose_name=_(u'Color'), max_length=7,
                             default='#6699bb', # без этого глючит farbtastic
                             help_text=_(u'HEX color, as #RRGGBB'))

    class Meta:
        verbose_name = _(u'Color')
        verbose_name_plural = _(u'Colors')
        ordering = ('title',)

    def __unicode__(self):
        return self.title

class Country(models.Model):
    """
    Definition of countries.
    """
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    iso2 = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3)

    class Meta:
        verbose_name = _(u'Country')
        verbose_name_plural = _(u'Countries')
        ordering = ('title',)

    def __unicode__(self):
        return self.title

class Producer(models.Model):
    """
    Definition of item's producers.
    """
    country = models.ForeignKey(Country, verbose_name=_(u'Country'))
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    slug = models.SlugField(max_length=80)

    class Meta:
        verbose_name = _(u'Producer')
        verbose_name_plural = _(u'Producers')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return u'/producer/%i/' % self.slug

class Item(models.Model):
    """
    Definition of items.
    """
    category = models.ForeignKey(Category, verbose_name=_(u'Category'))
    producer = models.ForeignKey(Producer, verbose_name=_(u'Producer'))
    color = models.ManyToManyField(Color, verbose_name=_(u'Color'))
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    slug = models.SlugField(max_length=80)
    price = models.FloatField(verbose_name=_(u'Price'))
    is_present = models.BooleanField(verbose_name=_(u'Is present'))
    desc = models.TextField(verbose_name=_(u'Description'), null=True, blank=True)
    image = models.ImageField(verbose_name=_(u'Image'), upload_to=u'itempics')
    tags = TagField(verbose_name=_(u'Tags'))
    registered = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Item')
        verbose_name_plural = _(u'Items')
        ordering = ('title',)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return u'/item/%s/' % self.slug

    def get_thumbnail_html(self):
        img = self.image
        img_resize_url = unicode(get_thumbnail(img, '100x100').url)
        html = '<a class="image-picker" href="%s"><img src="%s" alt="%s"/></a>'
        return html % (self.image.url, img_resize_url, self.title)
    get_thumbnail_html.short_description = _(u'Thumbnail')
    get_thumbnail_html.allow_tags = True

    def get_tag_list(self):
        return parse_tag_input(self.tags)

class Order(models.Model):
    """
    Definition of orders.
    """
    STATUSES = (
        ('1', _(u'Wait')),    # Ожидание
        ('2', _(u'Process')), # В обработке
        ('3', _(u'Sent')),    # Отправлено
        ('4', _(u'Cancel')),  # Отменено
        ('5', _(u'Closed')),  # Сделка завершена
        ('6', _(u'Undo')),    # Возврат
        )

    lastname = models.CharField(verbose_name=_(u'Lastname'), max_length=64)
    firstname = models.CharField(verbose_name=_(u'Firstname'), max_length=64)
    phone = models.CharField(verbose_name=_(u'Phone'), max_length=16)
    ship_to = models.CharField(verbose_name=_(u'Shipping address'), max_length=255)
    comment = models.TextField(blank=True, default=u'')
    totalprice = models.FloatField()
    discount = models.FloatField(default=0.0)
    count = models.PositiveIntegerField(default=0)
    status = models.CharField(verbose_name=_(u'Status'), max_length=2, choices=STATUSES)
    registered = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Order')
        verbose_name_plural = _(u'Orders')

    def __unicode__(self):
        return self.buyer.lastname

class OrderDetail(models.Model):
    """
    Definition of order's details.
    """
    order = models.ForeignKey(Order)
    item = models.ForeignKey(Item)
    count = models.PositiveIntegerField(default=0)
    price = models.FloatField()

    def __unicode__(self):
        return self.item.title

