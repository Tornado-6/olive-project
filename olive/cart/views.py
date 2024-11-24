from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from products.models import Product
from .models import Cart, CartItem
import logging

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'Added {product.name} to your cart.')
    return redirect('products:home')

@login_required
def remove_from_cart(request, item_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            cart_item.delete()
            cart = Cart.objects.get(user=request.user)
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart.',
                'cart_count': cart.item_count(),
                'cart_total': float(cart.total_price)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    else:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
        return redirect('cart:cart_detail')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            if quantity > 0 and quantity <= cart_item.product.stock:
                cart_item.quantity = quantity
                cart_item.save()
            elif quantity > cart_item.product.stock:
                cart_item.quantity = cart_item.product.stock
                cart_item.save()
                return JsonResponse({
                    'success': False,
                    'message': f'Only {cart_item.product.stock} items available.',
                    'updated_quantity': cart_item.quantity,
                    'item_total': float(cart_item.total_price),
                    'cart_total': float(cart_item.cart.total_price)
                })
            
            return JsonResponse({
                'success': True,
                'message': 'Cart updated successfully.',
                'item_total': float(cart_item.total_price),
                'cart_total': float(cart_item.cart.total_price)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    else:
        if quantity > 0 and quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
        elif quantity > cart_item.product.stock:
            messages.warning(request, f'Only {cart_item.product.stock} items available.')
            cart_item.quantity = cart_item.product.stock
            cart_item.save()
        
        return redirect('cart:cart_detail')

from rest_framework.decorators import api_view
@api_view(['GET'])
def cart_items_api(request):
    """API endpoint for mini cart items"""
    try:
        if not request.user.is_authenticated:
            return Response({'items': [], 'total': '0.00', 'item_count': 0})
        
        cart = Cart.objects.get_or_create(user=request.user)[0]
        items = []
        
        cart_items = cart.items.select_related('product').all()
        for item in cart_items:
            items.append({
                'id': item.id,
                'name': item.product.name,
                'price': str(item.product.price),
                'quantity': item.quantity,
                'total': str(item.total_price),
                'image_url': request.build_absolute_uri(item.product.image.url) if item.product.image else None
            })
        
        return Response({
            'items': items,
            'total': str(cart.total_price()),
            'item_count': cart.item_count()
        })
    except Exception as e:
        logger.error(f"Error in cart_items_api: {str(e)}")
        return Response(
            {'error': 'Error fetching cart items'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
