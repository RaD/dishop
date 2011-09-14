# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages import admin as fp_admin, models as fp_models

from shop import models

class WysiwygAdmin(admin.ModelAdmin):

    class Meta:
        wysiwyg_fields = ()

    class Media:
        js = ('%stiny_mce/tiny_mce.js' % settings.STATIC_URL,
              '%sjs/wysiwyg.js' % settings.STATIC_URL,)

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(WysiwygAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in self.Meta.wysiwyg_fields:
            field.widget.attrs['class'] = 'wysiwyg %s' % field.widget.attrs.get('class', '')
        return field

class WysiwygFlatPageAdmin(fp_admin.FlatPageAdmin, WysiwygAdmin):
    class Meta:
        wysiwyg_fields = ('content')

admin.site.unregister(fp_models.FlatPage)
admin.site.register(fp_models.FlatPage, WysiwygFlatPageAdmin)

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

class Product(WysiwygAdmin):
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

    class Meta:
        wysiwyg_fields = ('tech', 'desc',)

admin.site.register(models.Product, Product)

class Property(admin.ModelAdmin):
    list_display = ('product', 'key', 'value',)
admin.site.register(models.Property, Property)

class Detail(admin.TabularInline):
    model = models.OrderDetail
    extra = 0

class Order(admin.ModelAdmin):
    fieldsets = (
        (_(u'Customer'),
         {'fields': ('name', 'phone')}),
        (_(u'Order'),
         {'fields': ('totalprice', 'discount', )}),
        (_(u'Shipping'),
         {'fields': ('status', 'ship_to', 'comment')})
        )
    list_display = ('name', 'phone', 'status', 'totalprice', 'discount', 'registered')
    search_fields = ('name', 'status')
    inlines = [Detail]
admin.site.register(models.Order, Order)
