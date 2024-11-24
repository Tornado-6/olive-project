from django.urls import path
from . import views
import logging

logger = logging.getLogger(__name__)

app_name = 'products'

urlpatterns = [
    # Product views
    path('', views.home, name='home'),  # Root URL for product listing
    path('category/<int:category_id>/', views.category_view, name='category'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Product API endpoints
    path('api/products/<int:product_id>/', views.product_detail_api, name='product_detail_api'),
    path('api/products/<int:product_id>/reviews/', views.add_review, name='add_review'),
    path('api/reviews/<int:review_id>/', views.manage_review, name='manage_review'),
]

# Debug logging
logger.debug("Products URLs loaded: %s", urlpatterns)
