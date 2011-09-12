# -*- coding: utf-8 -*-
# (c) 2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('shop.views',
    url(r'^$', 'home', name='home'),
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^category/(?P<slug>[^/]+)/$', 'category', name='category'),
    url(r'^producer/(?P<slug>[^/]+)/$', 'producer', name='producer'),
    url(r'^product/(?P<slug>[^/]+)/$', 'product', name='product'),
    url(r'^cart/add/$', 'cart_add', name='cart_add'),
    url(r'^cart/del/$', 'cart_del', name='cart_del'),
    url(r'^cart/show/$', 'cart_show', name='cart_show'),
    url(r'^shipping/$', 'shipping', name='shipping'),
)

# обрабатка статики для devserver
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
