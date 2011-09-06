# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

"""
Модуль для дополнительных виджетов административного интерфейса.
"""

class ColorPickerWidget(forms.widgets.TextInput):
    """
    Класс для работы с модулем выбора цвета Farbtastic.
    """
    class Media:
        css = {
            'all': ('/static/farbtastic/farbtastic.css',)
            }
        js = ('/static/farbtastic/colorpicker.js',
              '/static/farbtastic/farbtastic.js',)

    def render(self, name, value, attrs=None):
        """ Метод рендеринга. """
        # base widget
        text_input_html = super(ColorPickerWidget, self).render(name, value, attrs)
        # own widget
        text_link_html = u'<a id="id_color_picker" href="#" onclick="return false;">%s</a>' % _(u'Palette')
        # join them together
        return mark_safe('%s %s' % (text_input_html, text_link_html))
