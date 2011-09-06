# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.db import models
from django.contrib.admin.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape

from datetime import datetime

from django_extensions.db.fields import UUIDField
from tagging.fields import TagField
from tagging.utils import parse_tag_input

from snippets import translit

class AbstractUUID(models.Model):
    """
    Abstract class to inject UUID as primary key.
    """
    uuid = UUIDField(verbose_name=_(u'Primary key'), primary_key=True, version=4)

    class Meta:
        abstract = True

class Category(AbstractUUID):
    """
    Definition of categories. May link on itself to make some kind of hierarchy.
    """
    parent = models.ForeignKey(u'self', verbose_name=_(u'Parent'), blank=True, null=True)
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    slug = models.SlugField(max_length=80)

    class Meta:
        verbose_name = _(u'Category')
        verbose_name_plural = _(u'Categories')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return u'/category/%s/' % self.slug

    def save(self):
        self.slug = translit(escape(self.title))
        super(Category, self).save()

class Color(AbstractUUID):
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

class Country(AbstractUUID):
    """
    Definition of countries.
    """
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    iso2 = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3)

    class Meta:
        verbose_name = _(u'Country')
        verbose_name_plural = _(u'Countries')

    def __unicode__(self):
        return self.title

class Producer(AbstractUUID):
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

class Item(AbstractUUID):
    """
    Definition of items.
    """
    category = models.ForeignKey(Category, verbose_name=_(u'Category'))
    producer = models.ForeignKey(Producer, verbose_name=_(u'Producer'))
    color = models.ManyToManyField(Color, verbose_name=_(u'Color'))
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    slug = models.SlugField(max_length=80)
    desc = models.TextField(verbose_name=_(u'Description'), null=True, blank=True)
    image = models.ImageField(verbose_name=_(u'Image'), upload_to=u'itempics')
    is_present = models.BooleanField(verbose_name=_(u'Is present'))
    registered = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)
    tags = TagField()

    class Meta:
        verbose_name = _(u'Item')
        verbose_name_plural = _(u'Items')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return u'/item/%s/' % self.slug


    def get_tag_list(self):
        return parse_tag_input(self.tags)

class Buyer(AbstractUUID):
    """
    Definition of buyers.
    """
    lastname = models.CharField(verbose_name=_(u'Lastname'), max_length=64)
    firstname = models.CharField(verbose_name=_(u'Firstname'), max_length=64)
    ship_to = models.CharField(verbose_name=_(u'Shipping address'), max_length=255)
    phone = models.CharField(verbose_name=_(u'Phone'), max_length=16)
    registered = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Buyer')
        verbose_name_plural = _(u'Buyers')

    def __unicode__(self):
        return u'%s %s' %(self.lastname, self.firstname,)

class Order(AbstractUUID):
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

    buyer = models.ForeignKey(Buyer)
    count = models.PositiveIntegerField(default=0)
    status = models.CharField(verbose_name=_(u'Status'), max_length=2, choices=STATUSES)
    totalprice = models.FloatField()
    discount = models.PositiveIntegerField(default=0)
    comment = models.TextField(blank=True, default=u'')
    registered = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Order')
        verbose_name_plural = _(u'Orders')

    def __unicode__(self):
        return self.buyer.lastname

class OrderDetail(AbstractUUID):
    """
    Definition of order's details.
    """
    order = models.ForeignKey(Order)
    item = models.ForeignKey(Item)
    count = models.PositiveIntegerField(default=0)
    price = models.FloatField()

    def __unicode__(self):
        return self.item.title

