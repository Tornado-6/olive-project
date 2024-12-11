from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import Wishlist
from products.models import Product
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.html import strip_tags

# Create your views here.


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(
                    request, "Account created successfully! Welcome to our store!"
                )
                return redirect("products:home")
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def user_login(request):
    next_page = request.GET.get("next", "products:home")

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect(next_page)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomAuthenticationForm()

    return render(
        request,
        "users/login.html",
        {
            "form": form,
            "next": next_page,
        },
    )


@login_required
def profile(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("users:profile")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "users/profile.html", {"form": form})


@login_required
def wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, "users/wishlist.html", {"wishlist": wishlist})


@api_view(["POST"])
@login_required
def add_to_wishlist(request, product_id):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)

    if product not in wishlist.products.all():
        wishlist.products.add(product)
        return Response({"success": True, "message": "Added to wishlist"})
    return Response({"success": False, "message": "Already in wishlist"})


@api_view(["POST"])
@login_required
def remove_from_wishlist(request, product_id):
    wishlist = get_object_or_404(Wishlist, user=request.user)
    product = get_object_or_404(Product, id=product_id)

    if product in wishlist.products.all():
        wishlist.products.remove(product)
        return Response({"success": True, "message": "Removed from wishlist"})
    return Response({"success": False, "message": "Not in wishlist"})


def user_logout(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out successfully.")
    return redirect("products:home")


def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email", "")
        User = get_user_model()
        user = User.objects.filter(Q(email=email)).first()
        if user:
            subject = "Password Reset Requested"
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse(
                    "users:password_reset_confirm",
                    kwargs={"uidb64": uid, "token": token},
                )
            )
            email_template = "users/password_reset_email.html"
            context = {
                "user": user,
                "reset_url": reset_url,
                "site_name": "Olive Store",
            }
            email_html = render_to_string(email_template, context)
            try:
                send_mail(
                    subject,
                    strip_tags(email_html),
                    "noreply@olivestore.com",
                    [user.email],
                    html_message=email_html,
                )
                return redirect("users:password_reset_done")
            except BadHeaderError:
                messages.error(request, "Invalid header found in email.")
        messages.success(
            request, "Password reset instructions have been sent if the email exists."
        )
        return redirect("users:password_reset_done")
    return render(request, "users/password_reset.html")


def password_reset_done(request):
    return render(request, "users/password_reset_done.html")


def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            if password1 and password2 and password1 == password2:
                user.set_password(password1)
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect("users:password_reset_complete")
            else:
                messages.error(request, "Passwords do not match.")
        return render(request, "users/password_reset_confirm.html")
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect("users:password_reset")


def password_reset_complete(request):
    return render(request, "users/password_reset_complete.html")
