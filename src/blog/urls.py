# -*- coding: utf-8 -*-
# (c) 2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('blog.views',
    url(r'^(?P<slug>.+)/$', 'entry', name='entry'),
    url(r'^$', 'home', name='home'),
)

# обрабатка статики для devserver
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
