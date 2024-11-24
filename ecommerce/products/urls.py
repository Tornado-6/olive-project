from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product views
    path('', views.home, name='home'),
    path('category/<int:category_id>/', views.category_view, name='category'),
    
    # Product API endpoints
    path('api/products/<int:product_id>/', views.product_detail_api, name='product_detail_api'),
    
    # Review API endpoints
    path('api/products/<int:product_id>/reviews/', views.add_review, name='add_review'),
    path('api/reviews/<int:review_id>/', views.manage_review, name='manage_review'),
]
