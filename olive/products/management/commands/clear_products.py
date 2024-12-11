from django.core.management.base import BaseCommand
from products.models import Product, Category
import shutil
import os
from django.conf import settings


class Command(BaseCommand):
    help = "Clear all product data and images"

    def handle(self, *args, **options):
        # Delete all products
        product_count = Product.objects.count()
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {product_count} products"))

        # Delete all categories
        category_count = Category.objects.count()
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {category_count} categories"))

        # Clear media/products directory
        products_media_dir = os.path.join(settings.MEDIA_ROOT, "products")
        if os.path.exists(products_media_dir):
            shutil.rmtree(products_media_dir)
            os.makedirs(products_media_dir)
            self.stdout.write(self.style.SUCCESS("Cleared products media directory"))

        self.stdout.write(
            self.style.SUCCESS("Successfully cleared all product data and images")
        )
