# -*- coding: utf-8 -*-
# (c) 2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template

from blog import models

def home(request):
    context = {
        'breadcrumb': [
            {'url': reverse('shop:home'), 'title': _(u'Home')},
            {'url': reverse('blog:home'), 'title': _(u'Blog')},
            ],
        'entries': models.Entry.objects.all(),
        }
    return direct_to_template(request, 'blog/object_list.html', context)


def entry(request, slug):
    entry = get_object_or_404(models.Entry, slug=slug)
    context = {
        'breadcrumb': [
            {'url': reverse('shop:home'), 'title': _(u'Home')},
            {'url': reverse('blog:home'), 'title': _(u'Blog')},
            {'url': entry.get_absolute_url(), 'title': entry.title},
            ],
        'entry': entry,
        }
    return direct_to_template(request, 'blog/entry.html', context)
