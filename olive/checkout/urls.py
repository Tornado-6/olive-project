from django.urls import path
from . import views

app_name = "checkout"

urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("success/", views.checkout_success, name="checkout_success"),
    path("cancel/", views.checkout_cancel, name="checkout_cancel"),
]
