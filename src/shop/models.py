# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.db import models
from django.contrib.admin.models import User
from django.core.urlresolvers import reverse
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
    is_active = models.BooleanField(verbose_name=_(u'Is active'))
    order = models.IntegerField(verbose_name=_(u'Order'), default=0)
    base_url = models.CharField(max_length=255)

    class Meta:
        verbose_name = _(u'Category')
        verbose_name_plural = _(u'Categories')
        ordering = ('order', 'title',)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:category', args=[self.slug])

    def diff(self):
        has_diff = False
        changed_fields = {}
        old = self.__class__.objects.get(pk=self.pk)
        for field in ('title',):
            model_value = getattr(old, field)
            new_value = getattr(self, field)
            if model_value != new_value:
                has_diff = True
                changed_fields[field] = {
                    'old': model_value,
                    'new': new_value,
                    }
        return has_diff, changed_fields

    def save(self, *args, **kwargs):
        """
        If model is updated with the same data, then ignore this.
        """
        out = []
        if self.pk:
            is_changed, changed_field = self.diff()
            out = changed_field
        super(Category, self).save(*args, **kwargs)
        return out

class Color(models.Model):
    """
    Definition of product's colors.
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
    Definition of product's producers.
    """
    country = models.ForeignKey(Country, verbose_name=_(u'Country'), blank=True, null=True)
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    slug = models.SlugField(max_length=80)

    class Meta:
        verbose_name = _(u'Producer')
        verbose_name_plural = _(u'Producers')
        ordering = ('title',)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:producer', args=[self.slug])

class Product(models.Model):
    """
    Definition of products.
    """
    category = models.ForeignKey(Category, verbose_name=_(u'Category'))
    producer = models.ForeignKey(Producer, verbose_name=_(u'Producer'), blank=True, null=True)
    color = models.ManyToManyField(Color, verbose_name=_(u'Color'), blank=True)
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    slug = models.SlugField(max_length=80)
    price = models.FloatField(verbose_name=_(u'Price'))
    is_active = models.BooleanField(verbose_name=_(u'Is present'))
    is_recommend = models.BooleanField(verbose_name=_(u'Recomendation'), default=False)
    is_fixed = models.BooleanField(verbose_name=_(u'Don\'t allow to change automaticly'), default=False)
    desc = models.TextField(verbose_name=_(u'Description'), null=True, blank=True)
    tech = models.TextField(verbose_name=_(u'Technical Info'), null=True, blank=True)
    image = models.ImageField(verbose_name=_(u'Image'), upload_to=u'itempics')
    tags = TagField(verbose_name=_(u'Tags'), blank=True)
    registered = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)
    base_url = models.CharField(max_length=255)
    order = models.IntegerField(verbose_name=_(u'Order'), default=0)

    class Meta:
        verbose_name = _(u'Product')
        verbose_name_plural = _(u'Products')
        ordering = ('title',)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:product', args=[self.slug])

    def diff(self):
        has_diff = False
        changed_fields = {}
        old = self.__class__.objects.get(pk=self.pk)
        for field in ('price', 'is_active', 'desc',):
            model_value = getattr(old, field)
            new_value = getattr(self, field)
            if model_value != new_value:
                has_diff = True
                changed_fields[field] = {
                    'old': model_value,
                    'new': new_value,
                    }
        return has_diff, changed_fields

    def save(self, *args, **kwargs):
        """
        If model is updated with the same data, then ignore this.
        """
        out = {}
        if self.pk:
            is_changed, changed_field = self.diff()
            out = changed_field
        super(Product, self).save(*args, **kwargs)
        return out

    def get_thumbnail(self, size):
        img = self.image
        return unicode(get_thumbnail(img, '%(size)ix%(size)i' % {'size': size,}).url)

    def get_thumbnail_38(self):
        return self.get_thumbnail(38)

    def get_thumbnail_64(self):
        return self.get_thumbnail(64)

    def get_thumbnail_150(self):
        return self.get_thumbnail(150)

    def get_thumbnail_250(self):
        return self.get_thumbnail(250)

    def get_thumbnail_html(self):
        img_resize_url = self.get_thumbnail(100)
        html = '<a class="image-picker" href="%s"><img src="%s" alt="%s"/></a>'
        return html % (self.image.url, img_resize_url, self.title)
    get_thumbnail_html.short_description = _(u'Thumbnail')
    get_thumbnail_html.allow_tags = True

    def get_color_squares(self):
        squares = []
        style = 'border: 1px solid #5B80B2; width: 10px; height: 10px; margin-right: 4px; float: left;'
        div = '<div style="%s background-color: %s">&nbsp;</div>'
        for item in self.color.all():
            squares.append( div % (style, item.color) )
        return u''.join(squares)
    get_color_squares.short_description = _(u'Color')
    get_color_squares.allow_tags = True

    def fill_properties(self, data):
        for key, value in data:
            Property(product=self, key=key, value=value).save()

    def get_properties(self):
        return self.property_set.all()

    def drop_properties(self):
        self.get_properties().delete()

    def get_tag_list(self):
        return parse_tag_input(self.tags)

class Property(models.Model):
    """
    Definition of product's property.
    """
    product = models.ForeignKey(Product)
    key = models.CharField(verbose_name=_(u'Title'), max_length=64)
    value = models.CharField(verbose_name=_(u'Value'), max_length=128)

    class Meta:
        verbose_name = _(u'Property')
        verbose_name_plural = _(u'Properties')
        ordering = ('key',)

    def __unicode__(self):
        return self.key

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
        ('7', _(u'Shipping')),# Доставка
        )

    name = models.CharField(verbose_name=_(u'Name'), max_length=80)
    phone = models.CharField(verbose_name=_(u'Phone'), max_length=16)
    ship_to = models.CharField(verbose_name=_(u'Shipping address'), max_length=255)
    comment = models.TextField(blank=True, default=u'')
    totalprice = models.FloatField()
    discount = models.FloatField(default=0.0)
    status = models.CharField(verbose_name=_(u'Status'), max_length=2, default='1', choices=STATUSES)
    registered = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Order')
        verbose_name_plural = _(u'Orders')

    def __unicode__(self):
        return self.name

class OrderDetail(models.Model):
    """
    Definition of order's details.
    """
    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)
    quantity = models.PositiveIntegerField(default=0)
    price = models.FloatField()

    def __unicode__(self):
        return self.product.title

