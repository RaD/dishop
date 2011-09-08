# -*- coding: utf-8 -*-
# (c) 2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _

from lxml import etree
from lxml.etree import tounicode

import urllib2

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
        (u'я', u'ya'),  (u' ', u'_'),
        )
    translit = value.lower()
    for symb_in, symb_out in TRANSTABLE:
        translit = translit.replace(symb_in, symb_out)
    return translit

class Command(NoArgsCommand):
    help = _(u'Download data from master site and make changes in project database.')

    HOST = 'http://supersvyaz.ru'

    def handle_noargs(self, *args, **options):
        main_page = MainPage(self.HOST, '/')

        # disable all categories first
        models.Category.objects.all().update(is_active=False)

        for base, url, title in main_page.categories():
            print u'\n%s: %s [%s]' % ( _(u'Category'), title, url)
            kwargs = { 'base_url': url, 'title': title, 'slug': translit(title), }
            try:
                obj = models.Category.objects.get(base_url=url)
            except models.Category.DoesNotExist:
                print '    [create]',
                obj = models.Category(**dict(kwargs, is_active=True))
            else:
                print '    [update]',
                if obj.diff(**kwargs):
                    obj.is_active = True
                else:
                    continue
            result = obj.save()
            if result:
                print '    %(old)s -> %(new)s' % result

            # cat_page = DescPage(self.HOST, category.url)
            # for desc in cat_page.short_description():
            #     print '\n=== D ===', desc.url, desc.title

            #     item_page = ItemPage(self.HOST, desc.url)
            #     for item in item_page.full_description():
            #         print '\n=== I ===', item.url, item.title

            #     break


        print 'ok'

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

    def retrieve_page(self, suffix=None):
        try:
            if suffix:
                page = urllib2.urlopen(self.url + suffix)
            else:
                page = urllib2.urlopen(self.url)
        except urllib2.HTTPError, e:
            print _(u'Cannot retrieve URL.\nHTTP Error Code: %s') % e.code
        except urllib2.URLError, e:
            print _(u'Cannot retrieve URL: %s') % e.reason[1]
        else:
            return page

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
                #print tounicode(item)
                url = item.xpath(".//div[@class='obj']/div[@class='left']/a/@href")[0]
                title = item.xpath(".//div[@class='obj']/div[@class='center']/h3/a/text()")[0]

                url = item.xpath(".//div[@class='obj']/div[@class='left']/a/@href")[0]
                #img = item.xpath(".//div[@class='obj']/div[@class='left']/a/img/@src")[0]
                title = item.xpath(".//div[@class='obj']/div[@class='center']/h3/a/text()")[0]
                price = item.xpath(".//div[@class='obj']//div[@class='price' or @class='price-no']/text()")[0]
                is_present = 0 == len(item.xpath(".//div[@class='obj']//div[@class='price-no']"))

                print url, title
                assert len(url) and len(title)
                yield ShortDesc(self.base, url, title)

class ItemPage(BasePage):

    def full_description(self):
        desc_list = self.tree_list[0].xpath("//div[@class='content shop-box']//tr")
        print 'F', len(desc_list)
        for item in desc_list:
            #print tounicode(item)
            img = item.xpath(".//div[@class='item-pic']/a/img/@src")[0]
            details = item.xpath(".//div[@id='item-details']/ul")[0]
            colors = item.xpath(".//div[@id='item-details']/ul")[1]
            params = item.xpath(".//div[@id='item-tech']//tr")[0]

            print url, img, title, price, is_present
            assert len(url) and len(title)
            yield ShortDesc(self.base, url, title, image=img)

class Category(object):

    def __init__(self, base, url, title):
        self.base = base
        self.url = url
        self.title = title
        return
        self.obj, created = models.ATCCategory.objects.get_or_create(
            code=self.code,
            defaults={'name': self.name}
        )

class ShortDesc(object):

    def __init__(self, base, url, title, *args, **kwargs):
        self.base = base
        self.url = url
        self.title = title

        for key, value in kwargs.items():
            setattr(self, key, value)

        return

