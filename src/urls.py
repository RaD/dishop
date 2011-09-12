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

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

urlpatterns += patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^shop/', include('shop.urls', namespace='shop')),
    url(r'^$', 'shop.views.home'),
)

# обрабатка статики для devserver
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
