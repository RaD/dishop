# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django import template
from django.utils.translation import ugettext_lazy as _

from shop import models

register = template.Library()

@register.inclusion_tag('shop/inclusion/categories.html')
def categories_tag():
    return {
        'categories': models.Category.objects.filter(parent__isnull=True, is_active=True)
    }

@register.inclusion_tag('shop/inclusion/item_list.html')
def recommendation_tag():
    limit = getattr(settings, 'SHOP_ITEMS_RECOMMENDED', 5)
    return {
        'widget_title': _(u'Good choice'),
        'product_list': models.Product.objects.filter(is_recommend=True, is_active=True)[:limit],
    }

@register.inclusion_tag('shop/inclusion/item_list.html')
def favorites_tag():
    limit = getattr(settings, 'SHOP_ITEMS_FAVORITES', 10)
    return {
        'widget_title': _(u'Favorites'),
        'product_list': models.Product.objects.filter(is_recommend=True, is_active=True)[:limit], # fixme
    }
