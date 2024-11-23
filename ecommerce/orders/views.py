from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from .forms import CheckoutForm
from cart.models import Cart

# Create your views here.

@login_required
def checkout(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                shipping_address=form.cleaned_data['shipping_address'],
                billing_address=form.cleaned_data.get('billing_address') or form.cleaned_data['shipping_address'],
                total_amount=cart.total_price,
            )
            
            # Create order items from cart
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Clear the cart
            cart.items.all().delete()
            
            # Redirect to payment
            return redirect('orders:payment', order_id=order.id)
    else:
        form = CheckoutForm()
    
    context = {
        'form': form,
        'cart': cart
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def payment(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    
    if request.method == 'POST':
        # Here you would integrate with a payment gateway
        # For now, we'll just mark the order as processing
        order.status = 'processing'
        order.save()
        messages.success(request, 'Order placed successfully!')
        return redirect('orders:order_confirmation', order_id=order.id)
    
    context = {
        'order': order
    }
    return render(request, 'orders/payment.html', context)

@login_required
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'orders/confirmation.html', {'order': order})

@login_required
def order_list(request):
    orders = request.user.orders.all()
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
