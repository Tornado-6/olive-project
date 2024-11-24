from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart

# Create your views here.

@login_required
def checkout(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    context = {
        'cart': cart,
    }
    return render(request, 'checkout/checkout.html', context)

def checkout_success(request):
    return render(request, 'checkout/success.html')

def checkout_cancel(request):
    return redirect('cart:cart_detail')
