# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from haystack import indexes, site
from shop import models

class ProductIndex(indexes.SearchIndex):
    title = indexes.CharField(model_attr='title')
    desc = indexes.CharField(document=True, use_template=True)
    tech = indexes.CharField(model_attr='tech')

site.register(models.Product, ProductIndex)
