from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Create a unique slug by appending parent's name if it exists
            if self.parent:
                self.slug = slugify(f"{self.parent.name}-{self.name}")
            else:
                self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name

    @property
    def full_name(self):
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    CONDITION_CHOICES = [
        ("NEW", "New"),
        ("USED_LIKE_NEW", "Used - Like New"),
        ("USED_GOOD", "Used - Good"),
        ("USED_FAIR", "Used - Fair"),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    specifications = models.JSONField(
        null=True, blank=True
    )  # Store detailed specs as JSON

    condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, default="NEW"
    )
    stock = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        if self.reviews.exists():
            return round(self.reviews.aggregate(models.Avg("rating"))["rating__avg"], 1)
        return 0

    @property
    def total_reviews(self):
        return self.reviews.count()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["price"]),
        ]


class Review(models.Model):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        get_user_model(), related_name="reviews", on_delete=models.CASCADE
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("product", "user")  # One review per product per user

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"
