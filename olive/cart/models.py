from django.db import models
from django.conf import settings
from products.models import Product
from users.models import CustomUser

# Create your models here.

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_price(self):
        """Calculate total price of all cart items"""
        return sum(item.total_price for item in self.items.all())
    
    def item_count(self):
        """Count total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        return self.quantity * self.product.price
    
    def save(self, *args, **kwargs):
        # Ensure quantity doesn't exceed product stock
        if self.quantity > self.product.stock:
            self.quantity = self.product.stock
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    class Meta:
        unique_together = ('cart', 'product')  # Prevent duplicate products in cart
