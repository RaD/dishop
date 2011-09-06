# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson

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

def columns(param, count):
    def cols(func):
        def wrapper(request, *args, **kwargs):
            context =  func(request, *args, **kwargs)
            if param in context:
                object_list = context.get(param, None)
                length = len(object_list)

                from math import ceil
                per_column = int(ceil(float(length)/count))
                column_list = []
                for i in range(count):
                    column_list.append(object_list[i*per_column:(i+1)*per_column])
                context['column_list'] = column_list
            return context
        return wrapper
    return cols

def paginate_by(object_name, page_name='page', count=getattr(settings, 'SHOP_ITEMS_PER_PAGE', 20)):
    def paged(func):
        def wrapper(request, *args, **kwargs):
            pagenum = int(kwargs.get(page_name, 1) or 1)
            del(kwargs[page_name])
            # получаем контекст
            context =  func(request, *args, **kwargs)
            if object_name in context:
                try:
                    objects = context.get(object_name)
                    ipp_settings = settings.SHOP_ITEMS_PER_PAGE
                    count = [ipp_settings, ipp_settings,
                             int(1.5 * ipp_settings),
                             int(2 * ipp_settings),
                             int(3 * ipp_settings)][int(request.session.get('howmuch_id', 1))]
                    paginator = Paginator(objects, count)

                    page = paginator.page(pagenum)

                    next_ten = pagenum + 10
                    if next_ten <= paginator.num_pages:
                        page.next_ten = next_ten

                    previous_ten = pagenum - 10
                    if previous_ten >= 1:
                        page.previous_ten = previous_ten

                    context['page'] = page
                    context[object_name] = paginator.page(pagenum).object_list
                except EmptyPage:
                    context[object_name] = paginator.page(paginator.num_pages).object_list
            return context
        return wrapper
    return paged

def ajax_processor(form_object=None):
    def processor(func):
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST':
                if form_object is not None:
                    form = form_object(request.POST)
                    if form.is_valid():
                        result = func(request, form, *args, **kwargs)
                    else:
                        if settings.DEBUG:
                            result = {'code': '301', 'desc': 'form is not valid : %s' % form.errors}
                        else:
                            result = {'code': '301', 'desc': 'Сервис временно отключен. Приносим свои извинения.'}
                else:
                    result = func(request, *args, **kwargs)
            else:
                if settings.DEBUG:
                    result = {'code': '401', 'desc': 'it must be POST'}
                else:
                    result = {'code': '401', 'desc': 'Не надо нас ломать, ну пожалуйста :)'}
            json = simplejson.dumps(result)
            return HttpResponse(json, mimetype="application/json")
        return wrapper
    return processor
