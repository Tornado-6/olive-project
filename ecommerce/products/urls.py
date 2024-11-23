from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<int:category_id>/', views.category_view, name='category'),
    path('api/products/<int:product_id>/', views.product_detail_api, name='product_detail_api'),
]
