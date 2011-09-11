# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from shop import models

class Category(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'slug', 'parent', 'is_active', 'order',)
    fieldsets = ( (None, {'fields': ('parent', 'title', 'slug', ('is_active', 'order'),)}), )
    search_fields = ('title',)
admin.site.register(models.Category, Category)

class Color(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'slug', 'colored_field',)
    ordering = ('title',)

    def colored_field(self, floor):
        """ Метод для раскраски поля с цветом. """
        return u'<div style="background-color: %s;">%s</div>' % (floor.color, floor.color)
    colored_field.short_model_desc = _(u'Color')
    colored_field.allow_tags = True

    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Метод для изменения виджета для поля определения цвета. """
        from widgets import ColorPickerWidget
        if db_field.name == 'color':
            kwargs['widget'] = ColorPickerWidget
        return super(Color, self).formfield_for_dbfield(db_field, **kwargs)
admin.site.register(models.Color, Color)

class Country(admin.ModelAdmin):
    list_display = ('iso2', 'iso3', 'title',)
admin.site.register(models.Country, Country)

class Producer(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'slug', 'country',)
    search_fields = ('title',)
admin.site.register(models.Producer, Producer)

class Item(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (_(u'Information'),
         {'fields':(('title', 'slug'),
                    ('category', 'producer'),
                    'color', 'price',
                    'is_active', 'is_recommend', 'is_fixed',
                    )}),
        (_(u'More info'),
         {'fields': ('image', 'desc', 'tech', 'tags')})
        )
    list_display = ('title', 'get_thumbnail_html', 'category', 'price', 'get_color_squares', 'is_recommend', 'is_active', 'is_fixed', 'registered',)
    search_fields = ('title', 'category')
    save_as = True
admin.site.register(models.Item, Item)

class Property(admin.ModelAdmin):
    list_display = ('item', 'key', 'value',)
admin.site.register(models.Property, Property)

class Order(admin.ModelAdmin):
    fieldsets = (
        (_(u'Customer'),
         {'fields': ('lastname', 'phone')}),
        (_(u'Order'),
         {'fields': ('totalprice', 'discount', 'count')}),
        (_(u'Shipping'),
         {'fields': ('status', 'ship_to', 'comment')})
        )
    list_display = ('lastname', 'phone', 'status', 'totalprice', 'discount', 'registered')
    search_fields = ('lastname', 'status')
admin.site.register(models.Order, Order)

