# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django import template

from shop import models

register = template.Library()

@register.inclusion_tag('shop/inclusion/categories.html')
def categories_tag():
    return {
        'categories': models.Category.objects.filter(parent__isnull=True)
    }
