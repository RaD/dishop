# -*- coding: utf-8 -*-
# (c) 2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from hcard import models

class Address(admin.ModelAdmin):
    list_display = ('country_name', 'region', 'locality', 'postal_code',)
    search_fields = ('country_name', 'locality', 'street_address', 'extended_address',)
admin.site.register(models.Address, Address)

