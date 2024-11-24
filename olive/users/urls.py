from django.urls import path
from . import views
from . import api

app_name = 'users'

urlpatterns = [
    # User authentication and profile
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Password reset
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),
    
    # Wishlist views
    path('wishlist/', views.wishlist, name='wishlist'),
    
    # Wishlist API endpoints
    path('api/wishlist/check/<int:product_id>/', api.check_wishlist, name='check_wishlist'),
    path('api/wishlist/add/<int:product_id>/', api.add_to_wishlist, name='add_to_wishlist'),
    path('api/wishlist/remove/<int:product_id>/', api.remove_from_wishlist, name='remove_from_wishlist'),
]
