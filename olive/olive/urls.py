"""
URL configuration for olive project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),  # Products app at root URL
    path('cart/', include('cart.urls')),
    path('users/', include('users.urls')),
    path('orders/', include('orders.urls')),
    path('checkout/', include('checkout.urls')),  # Add checkout URLs
    path('products/', RedirectView.as_view(url='/', permanent=False)),  # Redirect /products/ to /
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
