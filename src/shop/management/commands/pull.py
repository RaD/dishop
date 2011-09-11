# -*- coding: utf-8 -*-
# (c) 2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _

from lxml import etree
from lxml.etree import tounicode

import urllib2, re, time, random, sys

from shop import models

from datetime import date, timedelta

def translit(value):
    TRANSTABLE = (
        (u'а', u'a'),   (u'б', u'b'),   (u'в', u'v'),   (u'г', u'g'),
        (u'д', u'd'),   (u'е', u'e'),   (u'ё', u'yo'),  (u'ж', u'zh'),
        (u'з', u'z'),   (u'и', u'i'),   (u'й', u'j'),   (u'к', u'k'),
        (u'л', u'l'),   (u'м', u'm'),   (u'н', u'n'),   (u'о', u'o'),
        (u'п', u'p'),   (u'р', u'r'),   (u'с', u's'),   (u'т', u't'),
        (u'у', u'u'),   (u'ф', u'f'),   (u'х', u'h'),   (u'ц', u'ts'),
        (u'ч', u'ch'),  (u'ш', u'sh'),  (u'щ', u'sch'), (u'ъ', u'_'),
        (u'ы', u'yi'),  (u'ь', u''),    (u'э', u'e'),   (u'ю', u'yu'),
        (u'я', u'ya'),  (u' ', u'_'),   (u'/', u'_'),   (u':', u'_'),
        )
    translit = value.lower()
    for symb_in, symb_out in TRANSTABLE:
        translit = translit.replace(symb_in, symb_out)
    return translit

def remove_brackets(value):
    tpl = re.compile(r'^(\s?[^\(]+).*$')
    obj = tpl.match(value)
    if obj:
        return obj.groups(1)[0].strip()
    else:
        return None

class Command(NoArgsCommand):
    help = _(u'Download data from master site and make changes in project database.')

    HOST = 'http://supersvyaz.ru'

    def handle_noargs(self, *args, **options):
        main_page = MainPage(self.HOST, '/')

        # disable all categories first
        models.Category.objects.all().update(is_active=False)

        for c_index, data in enumerate(main_page.categories(), 1):
            base, url, title = data
            print u'\n%s: %s [%s]' % (_(u'Category'), title, url)
            stripped = remove_brackets(title)
            fields = { 'base_url': url, 'title': stripped, 'slug': translit(stripped), }
            category = self.fill(models.Category, c_index, fields)

            cat_page = DescPage(self.HOST, url)
            for i_index, desc in enumerate(cat_page.short_description(), 1):
                print '\n=== D === %(title)s, price is %(price)s' % desc

                item_title = desc.get('title')
                item_slug = translit(item_title)
                producer_title = item_title.split(' ')[0]
                producer = self.producer_goc(producer_title)

                data = {'category': category,
                        'producer': producer,
                        'base_url': desc.get('url'),
                        'title': item_title,
                        'slug': item_slug,
                        'price': desc.get('price'),
                        'is_active': desc.get('is_active'),
                        'desc': desc.get('desc'),
                        'tech': desc.get('tech'),
                        }

                obj = self.fill(models.Product, i_index, data)
                self.save_image(obj, self.HOST + desc.get('image'))
        print 'ok'

    def fill(self, model, index, fields):
        try:
            obj = model.objects.get(base_url=fields.get('base_url'))
            print 'update'
        except model.DoesNotExist:
            obj = model(**dict(fields, is_active=True, order=index*10))
            print 'create'
        else:
            is_changed, changed_field = obj.diff()
            if not is_changed:
                return obj
        obj.is_active = True
        result = obj.save()
        if result:
            print '    %(old)s -> %(new)s' % result
        return obj

    def producer_goc(self, title):
        slug = translit(title)
        try:
            obj = models.Producer.objects.get(slug=slug)
        except models.Producer.DoesNotExist:
            obj = models.Producer(title=title, slug=slug).save()
        return obj

    def save_image(self, obj, full_url):
        content = ContentFile(urllib2.urlopen(full_url).read())
        existed_image = obj.image
        if not existed_image:
            print 'Update image...',
            obj.image.save(full_url, content)
            print 'done'
        else:
            old_len = len(obj.image.read())
            new_len = len(content)
            print 'Update image...',
            if old_len != new_len:
                obj.image.save(full_url, content)
                print 'done'
            else:
                print 'skip'

class BasePage(object):

    parser = etree.HTMLParser()

    def __init__(self, base, href):
        self.base = base
        self.href = href
        self.page_urls = []
        self.tree_list = []

        tree = etree.parse(self.retrieve_page(), self.parser)
        self.tree_list.append(tree)

        if hasattr(self, 'paginator'):
            paginator = getattr(self, 'paginator', None)
            if paginator:
                for suffix in paginator():
                    tree = etree.parse(self.retrieve_page(suffix=suffix), self.parser)
                    self.tree_list.append(tree)

    def retrieve_page(self, url=None, suffix=None):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'utf-8;q=0.7,*;q=0.3',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'supersvyaz.ru',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.220 Safari/535.1',
            }

        if url:
            url = self.base + url
        else:
            url = self.url
        if suffix:
            url = url + suffix
        print 'Retrieve %s' % url
        while True:
            try:
                req = urllib2.Request(url, {}, headers)
                page = urllib2.urlopen(req)
                time.sleep(random.randint(5,20))
            except urllib2.HTTPError, e:
                print _(u'Cannot retrieve URL.\nHTTP Error Code: %s') % e.code
            except urllib2.URLError, e:
                print _(u'Cannot retrieve URL: %s') % e.reason[1]
            else:
                return page
            print 'Reconnect after 30 seconds'
            time.sleep(30)

    @property
    def url(self):
        return self.base+self.href

class MainPage(BasePage):

    def categories(self):
        tree = self.tree_list[0]
        link_list = tree.xpath("//div[@id='left-nav']/ul/li")
        for item in link_list:
            #print tounicode(item)
            url = item.xpath('./a/@href')[0]
            title = item.xpath('./a/text()')[0]
            assert len(url) and len(title)
            yield (self.base, url, title,)

class DescPage(BasePage):

    def paginator(self):
        if len(self.tree_list) > 1:
            return [] # не первый вход, игнорируем
        href_list = []
        link_list = self.tree_list[0].xpath("//div[@class='PageNav']//a")
        for item in link_list:
            href_list.append( item.xpath('./@href')[0] )
        return href_list

    def short_description(self):
        for tree in self.tree_list:
            desc_list = tree.xpath("//div[@class='content shop-box']//tr")
            for item in desc_list:
                data = {
                    'url': item.xpath(".//div[@class='obj']/div[@class='left']/a/@href")[0],
                    'title': item.xpath(".//div[@class='obj']/div[@class='center']/h3/a/text()")[0],
                    'price': item.xpath(".//div[@class='obj']//div[@class='price' or @class='price-no']/text()")[0],
                    'is_active': 0 == len(item.xpath(".//div[@class='obj']//div[@class='price-no']")),
                    }
                assert len(data.get('url', '')) and len(data.get('title', ''))
                data.update( self.full_description(data.get('url')) )
                yield data

    def full_description(self, url):
        tree = etree.parse(self.retrieve_page(url=url), self.parser)
        desc_list = tree.xpath("//div[@id='item-full']")
        assert len(desc_list), _(u'No elements found.')
        for item in desc_list:
            try:
                return {
                    'image': item.xpath(".//div[@class='item-pic']//img/@src")[0],
                    'desc': tounicode(item.xpath(".//div[@id='item-details']/ul")[0]),
                    'tech': tounicode(item.xpath(".//div[@id='item-tech']//table")[0]),
                    }
            except IndexError:
                with open(translit(url), 'w') as f:
                    f.write(tounicode(tree))
