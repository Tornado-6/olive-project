from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from products.models import Product
from .models import Wishlist

@login_required
def check_wishlist(request, product_id):
    """Check if a product is in user's wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    in_wishlist = wishlist.products.filter(id=product.id).exists()
    return JsonResponse({'in_wishlist': in_wishlist})

@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Add a product to user's wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    if not wishlist.products.filter(id=product.id).exists():
        wishlist.products.add(product)
        return JsonResponse({'success': True, 'message': 'Product added to wishlist'})
    return JsonResponse({'success': False, 'message': 'Product already in wishlist'})

@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Remove a product from user's wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    if wishlist.products.filter(id=product.id).exists():
        wishlist.products.remove(product)
        return JsonResponse({'success': True, 'message': 'Product removed from wishlist'})
    return JsonResponse({'success': False, 'message': 'Product not in wishlist'})
