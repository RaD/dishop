# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from shop import models

def trace_to(modulename, filename):
    import logging
    logging.basicConfig(level=logging.DEBUG,
                        filename=filename, filemode='a')
    def renderer(func):
        def wrapper(request, *args, **kw):
            logging.debug('%s:%s' % (modulename, func.__name__))
            return func(request, *args, **kw)
        return wrapper
    return renderer

def ajax_processor(form_object=None):
    def processor(func):
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST' and request.is_ajax:
                if not form_object:
                    result = func(request, *args, **kwargs)
                else:
                    form = form_object(request.POST)
                    if form.is_valid():
                        result = func(request, form, *args, **kwargs)
                    else:
                        if settings.DEBUG:
                            return HttpResponseBadRequest(unicode(form.errors))
                        else:
                            return HttpResponseBadRequest(_(u'Check sended data!'))
            else:
                return HttpResponseBadRequest(_(u'I wanna POST from AJAX!'))
            if type(result) is dict:
                json = simplejson.dumps(result)
                return HttpResponse(json, mimetype="application/json")
            else:
                return HttpResponse(result)
        return wrapper
    return processor

