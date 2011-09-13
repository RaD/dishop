# -*- coding: utf-8 -*-
# (c) 2009-2011 Ruslan Popov <ruslan.popov@gmail.com>

from django import forms
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import formset_factory

from haystack.forms import SearchForm

from shop import models, Cart

class CartAdd(forms.Form):
    product_id = forms.CharField(label=_(u'Product ID'), max_length=8)
    quantity = forms.IntegerField(label=_(u'Product Count'))
    redirect = forms.CharField(label=_(u'Redirect URL'), max_length=255)

    def save(self, request):
        pk = self.cleaned_data.get('product_id')
        quantity = self.cleaned_data.get('quantity')
        product = get_object_or_404(models.Product, pk=pk)
        return Cart().add(request, product, quantity)

class CartDel(forms.Form):
    product_id = forms.CharField(label=_(u'Product ID'), max_length=8)

    def save(self, request):
        pk = self.cleaned_data.get('product_id')
        return Cart().drop(request, int(pk))

class CartItem(forms.Form):
    pk = forms.IntegerField(label=_(u'Product ID'), widget=forms.HiddenInput)
    image = forms.CharField(label=_(u'Image URL'), max_length=255, required=False, widget=forms.HiddenInput)
    title = forms.CharField(label=_(u'Title'), max_length=64, required=False, widget=forms.HiddenInput)
    quantity = forms.IntegerField(label=_(u'Quantity'), widget=forms.TextInput(attrs={'size': 3}))
    price = forms.FloatField(label=_(u'Price'), required=False, widget=forms.HiddenInput)
    total = forms.FloatField(label=_(u'Total'), required=False, widget=forms.HiddenInput)

    def save(self, request):
        pk = self.cleaned_data.get('pk')
        quantity = self.cleaned_data.get('quantity')
        delete = self.cleaned_data.get('DELETE')

        if delete:
            Cart().drop(request, int(pk))
        else:
            product = get_object_or_404(models.Product, pk=pk)
            Cart().change(request, product, quantity)

CartFormSet = formset_factory(CartItem, extra=0, can_delete=True)

class Checkout(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ('name', 'phone', 'ship_to', 'comment',)

    def __init__(self, *args, **kwargs):
        super(Checkout, self).__init__(*args, **kwargs)
        self.fields['ship_to'].widget = forms.Textarea()

    def save(self, request):
        interface = Cart()
        cart = interface.state(request)

        order = models.Order(**dict(self.cleaned_data, totalprice=cart.get('price', 0.00)))
        order.save()

        for item in cart.get('object_list'):
            product = get_object_or_404(models.Product, pk=item.get('pk'))
            details = models.OrderDetail(order=order, product=product,
                                         quantity=item.get('quantity'),
                                         price=item.get('price'))
            details.save()

        interface.reset(request)

class Search(SearchForm):

    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        category_qs = models.Category.objects.all()
        category_ts = tuple( [(0, _(u'All categories'))] + [(c.pk, c.title) for c in category_qs] )
        self.fields['category'] = forms.ChoiceField(choices=category_ts, required=False)

    def search(self):
        sqs = super(Search, self).search()
        sqs = sqs.auto_query(self.cleaned_data['q'])
        if self.cleaned_data['category']:
            if self.cleaned_data['category'] != "0":
                sqs = sqs.filter(category__id=self.cleaned_data['category'])
        return sqs
