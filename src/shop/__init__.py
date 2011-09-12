# -*- coding: utf-8 -*-
# (c) 2011 Ruslan Popov <ruslan.popov@gmail.com>

from django.shortcuts import get_object_or_404, render

class Cart(object):

    def reset(self, request):
        request.session['cart'] = {}

    def add(self, request, product, quantity):

        if 'cart' not in request.session:
            self.reset(request)

        cart = request.session['cart']

        count = cart.get(product.pk, 0)
        cart[product.pk] = count + quantity
        request.session['cart'] = cart
        return self.html(request)

    def change(self, request, product, quantity):

        if 'cart' not in request.session:
            self.reset(request)

        cart = request.session['cart']
        cart[product.pk] = quantity
        request.session['cart'] = cart
        return self.html(request)

    def drop(self, request, pk):
        if 'cart' not in request.session:
            self.reset(request)

        cart = request.session['cart']
        del(cart[pk])
        request.session['cart'] = cart
        return self.html(request)


    def state(self, request):
        price = 0.0
        object_list = []

        if 'cart' not in request.session:
            self.reset(request)

        for pk, quantity in request.session['cart'].items():
            product = get_object_or_404(models.Product, pk=pk)
            object_list.append(
                {'pk': product.pk,
                 'title': product.title,
                 'price': product.price,
                 'url': product.get_absolute_url(),
                 'quantity': quantity,}
                )
            price += (product.price * quantity)
        return {'object_list': object_list, 'price': price,}

    def html(self, request):
        return render(request, 'shop/inclusion/cart.html',
                      self.state(request))
