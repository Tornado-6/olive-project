import os
import requests
import django
from django.conf import settings
from urllib.parse import urlparse

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from products.models import Product

# Unsplash API for getting relevant product images
UNSPLASH_ACCESS_KEY = 'YOUR_UNSPLASH_ACCESS_KEY'  # Replace with your key
UNSPLASH_API_URL = 'https://api.unsplash.com/search/photos'

def create_media_directory():
    """Create media directory if it doesn't exist"""
    media_root = settings.MEDIA_ROOT
    product_images_dir = os.path.join(media_root, 'product_images')
    os.makedirs(product_images_dir, exist_ok=True)
    return product_images_dir

def download_image(url, product_name, save_dir):
    """Download image from URL and save it"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Create a valid filename from product name
            filename = f"{product_name.lower().replace(' ', '_')}.jpg"
            filepath = os.path.join(save_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Return relative path from MEDIA_ROOT
            return os.path.join('product_images', filename)
    except Exception as e:
        print(f"Error downloading image for {product_name}: {str(e)}")
    return None

def get_placeholder_image_url(query):
    """Get a relevant image URL from Unsplash API"""
    try:
        headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}
        params = {
            'query': query,
            'per_page': 1,
            'orientation': 'landscape'
        }
        response = requests.get(UNSPLASH_API_URL, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                return data['results'][0]['urls']['regular']
    except Exception as e:
        print(f"Error fetching image from Unsplash: {str(e)}")
    
    # Fallback to placeholder.com if Unsplash fails
    return f"https://via.placeholder.com/800x600.jpg?text={query.replace(' ', '+')}"

def update_product_images():
    """Update all products with sample images"""
    products = Product.objects.all()
    images_dir = create_media_directory()
    
    for product in products:
        if not product.image or not os.path.exists(os.path.join(settings.MEDIA_ROOT, str(product.image))):
            print(f"Processing {product.name}...")
            
            # Use product name and description to get relevant image
            search_query = f"{product.name} {product.category.name}"
            image_url = get_placeholder_image_url(search_query)
            
            if image_url:
                image_path = download_image(image_url, product.name, images_dir)
                if image_path:
                    product.image = image_path
                    product.save()
                    print(f"Added image for {product.name}")
                else:
                    print(f"Failed to download image for {product.name}")
        else:
            print(f"Skipping {product.name} - image already exists")

if __name__ == '__main__':
    print("Starting to update product images...")
    update_product_images()
    print("Finished updating product images.")
