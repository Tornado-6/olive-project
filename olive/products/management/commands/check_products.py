from django.core.management.base import BaseCommand
from products.models import Product, Category
from django.db.models import Count

class Command(BaseCommand):
    help = 'Check product data quality'

    def handle(self, *args, **options):
        # Check for duplicate names
        duplicates = Product.objects.values('name').annotate(
            name_count=Count('name')
        ).filter(name_count__gt=1).order_by('-name_count')
        
        if duplicates:
            self.stdout.write(self.style.WARNING('\nFound duplicate product names:'))
            for dup in duplicates:
                self.stdout.write(f"'{dup['name']}' appears {dup['name_count']} times")
                products = Product.objects.filter(name=dup['name'])
                for p in products:
                    self.stdout.write(f"  - ID: {p.id}, Price: ₹{p.price}, Category: {p.category}")
        
        # Check for potentially problematic names
        problematic_names = Product.objects.filter(
            name__regex=r'^[0-9\s\(\)]+$|^[0-9]+[x\s\-]+[0-9]+$'
        )
        if problematic_names:
            self.stdout.write(self.style.WARNING('\nFound potentially problematic names:'))
            for p in problematic_names:
                self.stdout.write(f"'{p.name}' (ID: {p.id})")

        # Check for missing or short descriptions
        missing_desc = Product.objects.filter(description__isnull=True)
        short_desc = Product.objects.filter(description__regex=r'^.{1,20}$')
        
        if missing_desc:
            self.stdout.write(self.style.WARNING('\nProducts with missing descriptions:'))
            for p in missing_desc:
                self.stdout.write(f"'{p.name}' (ID: {p.id})")
        
        if short_desc:
            self.stdout.write(self.style.WARNING('\nProducts with very short descriptions:'))
            for p in short_desc:
                self.stdout.write(f"'{p.name}' (ID: {p.id}): '{p.description}'")

        # Check for missing images
        missing_images = Product.objects.filter(image='')
        if missing_images:
            self.stdout.write(self.style.WARNING('\nProducts with missing images:'))
            for p in missing_images:
                self.stdout.write(f"'{p.name}' (ID: {p.id})")

        # Print some statistics
        total_products = Product.objects.count()
        total_categories = Category.objects.count()
        products_with_images = Product.objects.exclude(image='').count()
        products_with_desc = Product.objects.exclude(description__isnull=True).count()

        self.stdout.write(self.style.SUCCESS('\nProduct Statistics:'))
        self.stdout.write(f"Total Products: {total_products}")
        self.stdout.write(f"Total Categories: {total_categories}")
        self.stdout.write(f"Products with Images: {products_with_images}")
        self.stdout.write(f"Products with Descriptions: {products_with_desc}")

        # Check category distribution
        self.stdout.write(self.style.SUCCESS('\nCategory Distribution:'))
        for cat in Category.objects.all():
            count = Product.objects.filter(category=cat).count()
            self.stdout.write(f"{cat.name}: {count} products")
