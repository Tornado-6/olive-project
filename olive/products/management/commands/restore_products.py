from django.core.management.base import BaseCommand
from products.models import Category, Product
from django.core.files.base import ContentFile
import requests
from decimal import Decimal

class Command(BaseCommand):
    help = 'Restores sample products and categories'

    def handle(self, *args, **kwargs):
        # Clear existing data
        Product.objects.all().delete()
        Category.objects.all().delete()

        # Create main categories
        olive_oils = Category.objects.create(
            name='Olive Oils',
            slug='olive-oils',
            description='Premium olive oils from around the world'
        )

        olives = Category.objects.create(
            name='Olives',
            slug='olives',
            description='Fresh and cured olives'
        )

        gifts = Category.objects.create(
            name='Gift Sets',
            slug='gift-sets',
            description='Curated olive oil gift sets'
        )

        # Create subcategories
        extra_virgin = Category.objects.create(
            name='Extra Virgin',
            slug='extra-virgin',
            description='Extra virgin olive oils',
            parent=olive_oils
        )

        infused = Category.objects.create(
            name='Infused Oils',
            slug='infused-oils',
            description='Flavored olive oils',
            parent=olive_oils
        )

        # Sample product data with placeholder images
        products = [
            {
                'name': 'Premium Extra Virgin Olive Oil',
                'slug': 'premium-extra-virgin-olive-oil',
                'category': extra_virgin,
                'price': Decimal('29.99'),
                'stock': 100,
                'description': 'Our flagship extra virgin olive oil, cold-pressed from the finest olives.',
                'image_url': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5',
                'specifications': {
                    'Origin': 'Greece',
                    'Acidity': '0.3%',
                    'Harvest': '2023',
                    'Size': '500ml'
                }
            },
            {
                'name': 'Garlic Infused Olive Oil',
                'slug': 'garlic-infused-olive-oil',
                'category': infused,
                'price': Decimal('24.99'),
                'stock': 75,
                'description': 'Rich olive oil infused with fresh garlic. Perfect for cooking and dipping.',
                'image_url': 'https://images.unsplash.com/photo-1476124369491-e7addf5db371',
                'specifications': {
                    'Base': 'Extra Virgin Olive Oil',
                    'Infusion': 'Fresh Garlic',
                    'Size': '250ml'
                }
            },
            {
                'name': 'Kalamata Olives',
                'slug': 'kalamata-olives',
                'category': olives,
                'price': Decimal('12.99'),
                'stock': 150,
                'description': 'Premium Kalamata olives from Greece, naturally cured.',
                'image_url': 'https://images.unsplash.com/photo-1593504049359-74330189a345',
                'specifications': {
                    'Origin': 'Kalamata, Greece',
                    'Type': 'Black olives',
                    'Size': '500g'
                }
            },
            {
                'name': 'Olive Oil Tasting Set',
                'slug': 'olive-oil-tasting-set',
                'category': gifts,
                'price': Decimal('89.99'),
                'stock': 30,
                'description': 'A curated selection of our finest olive oils for tasting.',
                'image_url': 'https://images.unsplash.com/photo-1595981267035-7b04ca84a82d',
                'specifications': {
                    'Contents': '3 x 250ml bottles',
                    'Varieties': 'Extra Virgin, Lemon Infused, Basil Infused',
                    'Packaging': 'Gift Box'
                }
            }
        ]

        # Create products
        for product_data in products:
            image_url = product_data.pop('image_url')
            try:
                # Download image from URL
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Create product
                    product = Product.objects.create(**product_data)
                    # Add image
                    image_name = f"{product.slug}.jpg"
                    product.image.save(image_name, ContentFile(response.content), save=True)
                    self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Failed to download image for {product_data["name"]}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating product {product_data["name"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully restored products and categories'))
