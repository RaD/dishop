# -*- coding: utf-8 -*-
# (c) 2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from blog import models

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

class Entry(WysiwygAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'is_active', 'allow_comments', 'registered',)
    fieldsets = ( (None, {'fields': ('title', 'slug', ('is_active', 'allow_comments'), 'content',)}), )
    search_fields = ('title',)

    class Meta:
        wysiwyg_fields = ('content')

admin.site.register(models.Entry, Entry)
