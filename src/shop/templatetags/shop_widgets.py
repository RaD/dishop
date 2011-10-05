# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django import template
from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages.models import FlatPage
from django.db.models import Q, F, Avg, Count

from itertools import chain

from shop import models, forms, Cart

register = template.Library()

@register.inclusion_tag('shop/inclusion/categories_list.html')
def categories_list_tag():
    return {
        'categories': models.Category.objects.filter(parent__isnull=True, is_active=True).exclude(product__isnull=True)
    }

@register.inclusion_tag('shop/inclusion/categories_select.html')
def categories_select_tag():
    return {
        'categories': models.Category.objects.filter(parent__isnull=True, is_active=True).exclude(product__isnull=True)
    }

@register.inclusion_tag('shop/inclusion/producers.html')
def producers_tag():
    return {
        'manufacturers': models.Producer.objects.exclude(product__isnull=True),
    }

@register.inclusion_tag('shop/inclusion/flatpage_list.html')
def flatpage_list_tag():
    return {
        'object_list': FlatPage.objects.all(),
    }

@register.inclusion_tag('shop/inclusion/cart.html', takes_context=True)
def cart_tag(context):
    return Cart().state(context['request'])

@register.inclusion_tag('shop/inclusion/item_list.html')
def recommendation_tag():
    limit = getattr(settings, 'SHOP_ITEMS_RECOMMENDED', 5)
    products = models.Product.objects.filter(is_recommend=True, is_active=True)[:limit]
    if 0 == len(products):
        # if no products were recommended then show random products there
        products = models.Product.objects.order_by('?').filter(is_active=True)[:limit]
    elif limit > len(products):
        # if we recommend lower that 'limit' products then add some random products there
        rest = limit - len(products)
        random_products = models.Product.objects.order_by('?').filter(is_active=True)[:rest]
        products = list(chain(products, random_products))
    return {
        'widget_title': _(u'Good choice'),
        'product_list': products,
    }


@register.inclusion_tag('shop/inclusion/item_list.html')
def favorites_tag():
    limit = getattr(settings, 'SHOP_ITEMS_FAVORITES', 10)
    annotated_products = models.OrderDetail.objects.values('product').annotate(count=Count('product')).order_by('-count')[:limit]
    if 0 == len(annotated_products):
        # if no products were buyed then show random products there
        products = models.Product.objects.order_by('?').filter(is_active=True)[:limit]
    else:
        pk_list = [i.get('product') for i in annotated_products]
        products = models.Product.objects.filter(pk__in=pk_list, is_active=True)
        if limit > len(products):
            # if we recommend lower that 'limit' products then add some random products there
            rest = limit - len(products)
            random_products = models.Product.objects.order_by('?').filter(is_active=True)[:rest]
            products = list(chain(products, random_products))
    return {
        'widget_title': _(u'Favorites'),
        'product_list': products,
    }

@register.inclusion_tag('shop/inclusion/search.html')
def search_widget_tag():
    return {
        'basic_search': forms.Search(),
    }
