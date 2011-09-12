# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template

from tagging.models import Tag
from tagging.utils import calculate_cloud

from shop import models, forms
from shop.forms_search import SearchForm, get_search_form as factory

from snippets import ajax_processor

def home(request):
    context = {
        'product_list': models.Product.objects.filter(is_active=True)[:settings.SHOP_LAST_INCOMING],
        }
    return direct_to_template(request, 'shop/home.html', context)

def contact(request):
    return direct_to_template(request, 'shop/base.html')

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
    return direct_to_template(request, 'shop/base.html')

def shipping(request):
    return direct_to_template(request, 'shop/base.html')


@ajax_processor(forms.CartAdd)
def cart_add(request, form):
    return form.save(request)

@ajax_processor(forms.CartDel)
def cart_del(request, form):
    return form.save(request)


def init_cart(request, force=False):
    """ Инициализация корзины. """
    if force or 'cart_items' not in request.session:
        request.session['cart_items'] = {}
        request.session['cart_count'] = 0
        request.session['cart_price'] = 0.00

def tag_search(request, tag):
    """ Функция для результатов поиска по тегу. """
    items = models.Item.objects.filter(Q(tags__search='%s' % tag))
    request.session['searchquery'] = tag
    request.session['cached_items'] = items # кэшируем для paginator
    return items

def get_search_forms(request):
    context = {
        'searchform': SearchForm(request.POST or None),
        'mainsearchform': factory('MainSearchForm', request.POST or None, initial={'is_present': True}),
        'sizesearchform': factory('SizeSearchForm', request.POST or None),
        }
    return context

def filter_items(request, model_name, items):
    """ Вспомогательная функция для получения более уточнённой выборки. """
    form = factory(model_name, data=request.POST)
    if form.is_valid():
        subset = form.search()
        # для inline моделей фильтр создаётся немного по другому, т.к. у них item.id
        if model_name == 'MainSearchForm':
            id_array = [i.id for i in subset]
        else:
            id_array = [i.item.id for i in subset]
        return (form, items.filter(id__in=id_array))
    else:
        return None

def get_search_results(request):
    if request.method == 'POST':
        full_search = 'simple' in request.POST and request.POST['simple'] == 'False'

        form = SearchForm(request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            # поиск по тексту
            if clean['userinput'] == u'':
                items = models.Item.objects.all()
            else:
                items = models.Item.objects.filter(Q(title__search=u'*"%s"*' % clean['userinput']) |
                                                   Q(desc__search=u'*"%s"*' % clean['userinput']) |
                                                   Q(tags__search=u'*"%s"*' % clean['userinput']))

            if full_search:
                model_name = None
                for key in ['MainSearchForm', 'SizeSearchForm']:
                    result = filter_items(request, key, items)
                    if not result: # форма не прошла проверка
                        return None
                    (form, items) = result
                    if key == 'MainSearchForm':
                        obj = form.cleaned_data['item_type']
                        if obj:
                            model_name = obj.model_name
                if model_name:
                    result = filter_items(request, model_name, items)
                    if not result: # форма не прошла проверка
                        return None
                    (form, items) = result

            request.session['searchquery'] = clean['userinput']
            request.session['howmuch_id'] = clean['howmuch']
            request.session['cached_items'] = items # кэшируем для paginator
            models.SearchStatQuery(request=request).save() # сохраняем запрос для статистики
        else:
            request.session['error'] = ('simple', request.POST,
                                        u'Ошибка во введённых данных. Проверьте их правильность.')
            return None
    else: # обращение через paginator
        items = request.session.get('cached_items', None)
    return items

def get_cart_items(request):
    """ Возвращаем содержимое корзины. """
    cart = request.session.get('cart_items', {})
    if len(cart) == 0:
        items = None
    else:
        items = []
        for i in cart:
            record = models.Item.objects.get(id=i)
            items.append(CartItem(record, cart[i]['count'], cart[i]['price']))
    return items

