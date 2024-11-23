import os
import django
import shutil
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from products.models import Category, Product

def download_image(url):
    """Download image from URL and create a Django File object"""
    img_temp = NamedTemporaryFile(delete=True)
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Write the image to temp file
            for block in response.iter_content(1024 * 8):
                if not block:
                    break
                img_temp.write(block)
            img_temp.flush()
            return File(img_temp)
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
    return None

def create_sample_data():
    """Create sample categories and products"""
    # Sample product data with image URLs
    sample_products = [
        {
            'category': 'Electronics',
            'products': [
                {
                    'name': 'Smartphone X',
                    'description': 'Latest smartphone with advanced features',
                    'price': 999.99,
                    'stock': 50,
                    'image_url': 'https://picsum.photos/800/600?random=1'
                },
                {
                    'name': 'Laptop Pro',
                    'description': 'High-performance laptop for professionals',
                    'price': 1499.99,
                    'stock': 30,
                    'image_url': 'https://picsum.photos/800/600?random=2'
                }
            ]
        },
        {
            'category': 'Clothing',
            'products': [
                {
                    'name': 'Classic T-Shirt',
                    'description': 'Comfortable cotton t-shirt',
                    'price': 24.99,
                    'stock': 100,
                    'image_url': 'https://picsum.photos/800/600?random=3'
                },
                {
                    'name': 'Denim Jeans',
                    'description': 'Premium quality denim jeans',
                    'price': 79.99,
                    'stock': 75,
                    'image_url': 'https://picsum.photos/800/600?random=4'
                }
            ]
        },
        {
            'category': 'Home & Garden',
            'products': [
                {
                    'name': 'Smart LED Bulb',
                    'description': 'WiFi-enabled LED bulb',
                    'price': 29.99,
                    'stock': 150,
                    'image_url': 'https://picsum.photos/800/600?random=5'
                },
                {
                    'name': 'Garden Tool Set',
                    'description': 'Complete set of essential garden tools',
                    'price': 89.99,
                    'stock': 40,
                    'image_url': 'https://picsum.photos/800/600?random=6'
                }
            ]
        },
        {
            'category': 'Books',
            'products': [
                {
                    'name': 'Python Programming',
                    'description': 'Learn Python programming from scratch',
                    'price': 39.99,
                    'stock': 100,
                    'image_url': 'https://picsum.photos/800/600?random=7'
                }
            ]
        },
        {
            'category': 'Home & Kitchen',
            'products': [
                {
                    'name': 'Coffee Maker',
                    'description': 'Automatic coffee maker with timer',
                    'price': 79.99,
                    'stock': 45,
                    'image_url': 'https://picsum.photos/800/600?random=8'
                }
            ]
        }
    ]

    print("Creating sample categories and products...")
    
    for category_data in sample_products:
        # Create category
        category, created = Category.objects.get_or_create(
            name=category_data['category']
        )
        if created:
            print(f"Created category: {category.name}")
        
        # Create products for this category
        for product_data in category_data['products']:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'category': category,
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'stock': product_data['stock']
                }
            )
            
            # Always update the image, even if product exists
            image_file = download_image(product_data['image_url'])
            if image_file:
                product.image.save(
                    f"{product.name.lower().replace(' ', '_')}.jpg",
                    image_file,
                    save=True
                )
                print(f"Added/Updated image for {product.name}")
            else:
                print(f"Failed to download image for {product.name}")

create_sample_data()
print("Sample data created successfully!")
