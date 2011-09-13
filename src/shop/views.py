# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from django.contrib.flatpages.models import FlatPage

from tagging.models import Tag
from tagging.utils import calculate_cloud

from shop import models, forms, Cart
from shop.forms_search import SearchForm, get_search_form as factory

from snippets import ajax_processor

def home(request):
    context = {
        'product_list': models.Product.objects.filter(is_active=True)[:settings.SHOP_LAST_INCOMING],
        }
    return direct_to_template(request, 'shop/home.html', context)

def category(request, slug):
    category = get_object_or_404(models.Category, slug=slug)
    context = {
        'category': category,
        'breadcrumb': [
            {'url': reverse('shop:home'), 'title': _('Home')},
            {'url': category.get_absolute_url(), 'title': category.title},
            ],
        }
    return direct_to_template(request, 'shop/category.html', context)

def producer(request, slug):
    producer = get_object_or_404(models.Producer, slug=slug)
    context = {
        'producer': producer,
        'breadcrumb': [
            {'url': reverse('shop:home'), 'title': _('Home')},
            {'url': producer.get_absolute_url(), 'title': producer.title},
            ],
        }
    return direct_to_template(request, 'shop/producer.html', context)

def product(request, slug):
    product = get_object_or_404(models.Product, slug=slug)
    context = {
        'product': product,
        'breadcrumb': [
            {'url': reverse('shop:home'), 'title': _('Home')},
            {'url': product.category.get_absolute_url(), 'title': product.category.title},
            {'url': product.get_absolute_url(), 'title': product.title},
            ],
        }
    return direct_to_template(request, 'shop/product.html', context)

def cart_show(request):
    cart = Cart().state(request)
    object_list = []
    for el in cart.get('object_list'):
        product = get_object_or_404(models.Product, pk=el.get('pk'))
        object_list.append( dict(el,
                                 image=product.get_thumbnail_64(),
                                 total=el.get('price')*el.get('quantity')) )
    cart['object_list'] = object_list

    formset = forms.CartFormSet(request.POST or None, initial=object_list)
    if formset.is_valid():
        for form in formset:
            form.save(request)
        return redirect('shop:cart_show')

    context = {
        'breadcrumb': [
            {'url': reverse('shop:home'), 'title': _(u'Home')},
            {'url': reverse('shop:cart_show'), 'title': _(u'Shopping Cart')},
            ],
        'cart': cart,
        'formset': formset,
        }
    return direct_to_template(request, 'shop/cart_list.html', context)

def checkout(request):
    form = forms.Checkout(request.POST or None)
    if form.is_valid():
        form.save(request)
        return redirect('shop:status')
    context = {
        'form': form,
        }
    return direct_to_template(request, 'shop/checkout.html', context)

def status(request):
    return direct_to_template(request, 'shop/status.html')

def flatpage(request):
    page = get_object_or_404(FlatPage, url__exact=request.path)
    context = {
        'breadcrumb': [
            {'url': reverse('shop:home'), 'title': _(u'Home')},
            {'url': page.url, 'title': page.title},
            ],
        'page': page,
        }
    return direct_to_template(request, 'shop/flatpage.html', context)


@ajax_processor(forms.CartAdd)
def cart_add(request, form):
    return form.save(request)

@ajax_processor(forms.CartDel)
def cart_del(request, form):
    return form.save(request)

def lookup(request):
    form = forms.Search(request.POST)
    context = {
        'form': form,
        'breadcrumb': [
            {'url': reverse('shop:home'), 'title': _(u'Home')},
            {'url': 'javascript:false;', 'title': _(u'Search Results')},
            ],
        }
    if form.is_valid():
        context['object_list'] = [p.object for p in form.search()]
    return direct_to_template(request, 'shop/lookup.html', context)
