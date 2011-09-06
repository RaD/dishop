# -*- coding: utf-8 -*-
# (c) 2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('')

if settings.DEBUG:
    urlpatterns += patterns(
    '',
    # разрешаем вывод документации по проекту
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    )

urlpatterns += patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
)

# обрабатка статики для devserver
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
