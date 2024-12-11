from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from cart.models import Cart
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.


@login_required
def checkout(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]

    if request.method == "POST":
        try:
            # Create line items for each cart item
            line_items = []
            for item in cart.items.all():
                line_items.append(
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": int(
                                item.product.price * 100
                            ),  # Convert to cents
                            "product_data": {
                                "name": item.product.name,
                                "description": (
                                    item.product.description[:500]
                                    if item.product.description
                                    else None
                                ),  # Stripe has a 500 char limit
                                "images": (
                                    [request.build_absolute_uri(item.product.image.url)]
                                    if item.product.image
                                    else []
                                ),
                            },
                        },
                        "quantity": item.quantity,
                    }
                )

            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=request.build_absolute_uri(
                    reverse("checkout:checkout_success")
                ),
                cancel_url=request.build_absolute_uri(
                    reverse("checkout:checkout_cancel")
                ),
                customer_email=request.user.email,
            )
            return redirect(checkout_session.url)

        except Exception as e:
            return render(request, "checkout/error.html", {"error": str(e)})

    context = {
        "cart": cart,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, "checkout/checkout.html", context)


def checkout_success(request):
    # Clear the cart after successful payment
    if request.user.is_authenticated:
        cart = Cart.objects.get_or_create(user=request.user)[0]
        cart.items.all().delete()
    return render(request, "checkout/success.html")


def checkout_cancel(request):
    return redirect("cart:cart_detail")
