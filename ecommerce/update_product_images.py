import os
import django
import requests
from PIL import Image
from io import BytesIO
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from products.models import Product
from django.core.files import File

def download_image(url, filename):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            # Resize image to a reasonable size
            max_size = (800, 800)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            # Save to BytesIO
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            img_io.seek(0)
            return File(img_io, name=filename)
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def update_product_images():
    # Dictionary mapping product names/descriptions to appropriate image URLs
    image_urls = {
        'Laptop': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853',
        'Smartphone': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97',
        'Headphones': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e',
        'Camera': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32',
        'Watch': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30',
        'Tablet': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0',
        'Speaker': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1',
        'Gaming Console': 'https://images.unsplash.com/photo-1486401899868-0e435ed85128',
        'Drone': 'https://images.unsplash.com/photo-1473968512647-3e447244af8f',
        'VR Headset': 'https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac',
        'Garden Tool': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b',
        'LED Bulb': 'https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85',
        'Smart Bulb': 'https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85',
        'Jeans': 'https://images.unsplash.com/photo-1542272604-787c3835535d',
        'T-Shirt': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab',
        'Coffee Maker': 'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6',
        'Programming': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6',
        'Book': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6'
    }

    products = Product.objects.all()
    for product in products:
        # Try to find a matching image URL based on product name or description
        matching_key = None
        for key in image_urls:
            if key.lower() in product.name.lower() or key.lower() in product.description.lower():
                matching_key = key
                break
        
        if matching_key:
            print(f"Updating image for {product.name}")
            image_url = image_urls[matching_key]
            filename = f"{product.name.lower().replace(' ', '_')}.jpg"
            image_file = download_image(image_url, filename)
            
            if image_file:
                # Delete old image if it exists
                if product.image:
                    try:
                        product.image.delete(save=False)
                    except Exception as e:
                        print(f"Error deleting old image: {e}")
                
                # Save new image
                product.image = image_file
                product.save()
                print(f"Successfully updated image for {product.name}")
            else:
                print(f"Failed to download image for {product.name}")
        else:
            print(f"No matching image found for {product.name}")
        
        # Add a small delay to avoid rate limiting
        time.sleep(1)

if __name__ == '__main__':
    print("Starting product image update...")
    update_product_images()
    print("Finished updating product images.")
