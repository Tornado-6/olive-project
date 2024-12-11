from .models import Cart


def cart_processor(request):
    """Make cart data available to all templates."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.select_related("product").all()
        return {
            "cart": cart,
            "cart_items": cart_items,
        }
    return {
        "cart": None,
        "cart_items": [],
    }
