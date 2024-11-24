from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.text import slugify
from products.models import Product, Category
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import pytesseract
import io
import re
import logging
import json
from pathlib import Path
from decimal import Decimal
import random
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress PIL and Tesseract debug output
logging.getLogger('PIL').setLevel(logging.WARNING)

class PDFPageProcessor:
    """Handles the processing of individual PDF pages."""
    
    def __init__(self):
        self.image_quality = {
            'dpi': 300,
            'scale_factor': 2,
            'enhance_factor': 1.5
        }
    
    def preprocess_image(self, image):
        """Apply advanced image preprocessing techniques."""
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Apply CLAHE for better contrast
        lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        enhanced = cv2.cvtColor(cv2.merge((cl,a,b)), cv2.COLOR_LAB2BGR)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoisingColored(enhanced)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        return sharpened
    
    def extract_text_regions(self, image):
        """Extract text regions using advanced segmentation."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find text regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        dilated = cv2.dilate(binary, kernel, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h > 100:  # Filter out noise
                text_regions.append((x, y, w, h))
        
        return text_regions
    
    def extract_product_images(self, image):
        """Extract product images with improved quality."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        images = []
        min_area = image.shape[0] * image.shape[1] * 0.02
        max_area = image.shape[0] * image.shape[1] * 0.4
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            if min_area <= area <= max_area and 0.5 <= w/h <= 2.0:
                # Extract with padding
                padding = 20
                y1 = max(0, y - padding)
                y2 = min(image.shape[0], y + h + padding)
                x1 = max(0, x - padding)
                x2 = min(image.shape[1], x + w + padding)
                
                roi = image[y1:y2, x1:x2]
                
                # Enhance image quality
                enhanced = self.enhance_product_image(roi)
                images.append(enhanced)
        
        return images
    
    def enhance_product_image(self, image):
        """Apply advanced image enhancement techniques."""
        # Convert to PIL Image
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Enhance color
        enhancer = ImageEnhance.Color(pil_image)
        enhanced = enhancer.enhance(1.2)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = enhancer.enhance(1.3)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(enhanced)
        enhanced = enhancer.enhance(1.5)
        
        # Save with high quality
        img_buffer = io.BytesIO()
        enhanced.save(img_buffer, format='PNG', quality=95, optimize=True)
        return Image.open(img_buffer)

class ProductInformationExtractor:
    """Handles extraction and validation of product information."""
    
    def __init__(self):
        self.price_ranges = {
            'premium': (299.99, 999.99),
            'standard': (99.99, 299.99),
            'basic': (29.99, 99.99)
        }
    
    def clean_text(self, text):
        """Clean and normalize extracted text."""
        # Remove special characters and normalize whitespace
        text = re.sub(r'[^\w\s\-.,()]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_product_info(self, text):
        """Extract structured product information from text."""
        products = []
        lines = text.split('\n')
        current_product = {}
        
        for line in lines:
            line = self.clean_text(line)
            
            if not line:
                continue
            
            # Identify product name
            if self.is_product_name(line):
                if current_product:
                    products.append(current_product)
                current_product = {'name': line}
                continue
            
            # Extract dimensions if present
            dimensions = self.extract_dimensions(line)
            if dimensions and current_product:
                current_product['dimensions'] = dimensions
            
            # Extract other specifications
            specs = self.extract_specifications(line)
            if specs and current_product:
                current_product.update(specs)
        
        # Add last product
        if current_product:
            products.append(current_product)
        
        return products
    
    def is_product_name(self, text):
        """Determine if text is likely a product name."""
        # Product names typically start with capital letters
        # and contain 3-50 characters
        if not (3 <= len(text) <= 50):
            return False
            
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', text):
            return False
            
        # Shouldn't be just measurements
        if re.match(r'^[\d\s\-x×\.]+(?:mm|cm|m|mtr\.?)?$', text):
            return False
            
        return True
    
    def extract_dimensions(self, text):
        """Extract product dimensions from text."""
        dimension_pattern = r'(\d+(?:\.\d+)?)\s*(?:x|×)\s*(\d+(?:\.\d+)?)\s*(?:x|×)\s*(\d+(?:\.\d+)?)\s*(mm|cm|m)?'
        match = re.search(dimension_pattern, text)
        
        if match:
            width, height, depth, unit = match.groups()
            return {
                'width': float(width),
                'height': float(height),
                'depth': float(depth),
                'unit': unit or 'mm'
            }
        return None
    
    def extract_specifications(self, text):
        """Extract product specifications from text."""
        specs = {}
        
        # Extract material
        material_match = re.search(r'material:?\s*([^,\.]+)', text, re.I)
        if material_match:
            specs['material'] = material_match.group(1).strip()
        
        # Extract color/finish
        color_match = re.search(r'(?:color|finish):?\s*([^,\.]+)', text, re.I)
        if color_match:
            specs['color'] = color_match.group(1).strip()
        
        return specs

class Command(BaseCommand):
    help = 'Import products from a PDF catalog with advanced processing'
    
    def add_arguments(self, parser):
        parser.add_argument('pdf_path', type=str, help='Path to the PDF catalog')
        parser.add_argument('--default-stock', type=int, default=10)
        parser.add_argument('--skip-clear', action='store_true')
    
    def handle(self, *args, **options):
        pdf_path = options['pdf_path']
        
        if not options['skip_clear']:
            self.clear_existing_data()
        
        self.ensure_category_structure()
        
        # Initialize processors
        page_processor = PDFPageProcessor()
        info_extractor = ProductInformationExtractor()
        
        try:
            # Convert PDF to images
            pages = convert_from_path(pdf_path, dpi=300)
            
            for i, page in enumerate(pages, 1):
                self.stdout.write(f"Processing page {i} of {len(pages)}...")
                
                # Preprocess page
                processed_image = page_processor.preprocess_image(page)
                
                # Extract text regions
                text_regions = page_processor.extract_text_regions(processed_image)
                
                # Extract text from regions
                texts = []
                for x, y, w, h in text_regions:
                    region = processed_image[y:y+h, x:x+w]
                    text = pytesseract.image_to_string(region)
                    texts.append(text)
                
                # Extract product information
                products = info_extractor.extract_product_info('\n'.join(texts))
                
                # Extract and assign images
                product_images = page_processor.extract_product_images(processed_image)
                
                # Create products
                for product_info in products:
                    self.create_product(product_info, product_images)
            
            self.stdout.write(self.style.SUCCESS("PDF catalog import completed successfully"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing PDF: {str(e)}"))
            raise CommandError(str(e))
    
    def create_product(self, product_info, images):
        """Create a product with extracted information."""
        try:
            # Generate slug
            slug = slugify(product_info['name'])
            
            # Determine category
            category = self.categorize_product(product_info)
            
            # Create product
            product = Product.objects.create(
                name=product_info['name'],
                slug=slug,
                category=category,
                price=self.generate_price(product_info),
                stock=10,
                description=self.generate_description(product_info)
            )
            
            # Assign first available image
            if images:
                image = images[0]
                image_name = f"{slug}.png"
                image_io = io.BytesIO()
                image.save(image_io, format='PNG', quality=95)
                product.image.save(image_name, ContentFile(image_io.getvalue()), save=True)
            
            self.stdout.write(f"Created product: {product.name}")
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Failed to create product {product_info['name']}: {str(e)}"))
    
    def categorize_product(self, product_info):
        """Determine product category based on extracted information."""
        # Get default category
        try:
            default_category = Category.objects.get(name='Storage Solutions')
            default_subcategory = Category.objects.get(name='Custom Storage', parent=default_category)
        except Category.DoesNotExist:
            self.stdout.write(self.style.WARNING("Default category not found, creating it..."))
            default_category = Category.objects.create(name='Storage Solutions')
            default_subcategory = Category.objects.create(name='Custom Storage', parent=default_category)
        
        # Extract text for matching
        name = product_info.get('name', '').lower()
        material = product_info.get('material', '').lower()
        
        # Category mapping with keywords
        category_mapping = {
            'Storage Solutions': {
                'Baskets': ['basket', 'wire', 'wicker'],
                'Pullouts': ['pullout', 'pull-out', 'drawer'],
                'Corner Units': ['corner', 'l-shape'],
                'Pantry Units': ['pantry', 'food storage'],
            },
            'Hardware': {
                'Handles & Knobs': ['handle', 'knob', 'pull'],
                'Hinges': ['hinge', 'pivot'],
                'Slides & Rails': ['slide', 'rail', 'channel'],
            },
            'Kitchen Solutions': {
                'General Storage': ['kitchen', 'utensil', 'cutlery'],
                'Pantry Solutions': ['pantry', 'food', 'storage'],
                'Corner Solutions': ['corner', 'lazy susan'],
            }
        }
        
        # Try to find matching category
        for main_cat, subcats in category_mapping.items():
            try:
                main_category = Category.objects.get(name=main_cat)
                for subcat_name, keywords in subcats.items():
                    if any(keyword in name or keyword in material for keyword in keywords):
                        try:
                            return Category.objects.get(name=subcat_name, parent=main_category)
                        except Category.DoesNotExist:
                            continue
            except Category.DoesNotExist:
                continue
        
        return default_subcategory
    
    def generate_price(self, product_info):
        """Generate realistic price based on product information."""
        name = product_info.get('name', '').lower()
        
        # Base price ranges for different product types
        price_ranges = {
            'premium': {
                'min': 15000,
                'max': 50000,
                'keywords': ['system', 'complete', 'set', 'premium']
            },
            'standard': {
                'min': 5000,
                'max': 15000,
                'keywords': ['basket', 'pullout', 'storage']
            },
            'basic': {
                'min': 1000,
                'max': 5000,
                'keywords': ['handle', 'knob', 'accessory']
            }
        }
        
        # Determine price tier
        selected_range = price_ranges['standard']  # default to standard
        for tier, details in price_ranges.items():
            if any(keyword in name for keyword in details['keywords']):
                selected_range = details
                break
        
        # Generate random price within range
        price = random.uniform(selected_range['min'], selected_range['max'])
        
        # Round to nearest 100
        price = round(price / 100) * 100
        
        return Decimal(str(price))
    
    def generate_description(self, product_info):
        """Generate product description from extracted information."""
        description_parts = []
        
        # Add name
        name = product_info.get('name', '')
        if name:
            description_parts.append(name)
        
        # Add dimensions if available
        if 'dimensions' in product_info:
            dim = product_info['dimensions']
            description_parts.append(
                f"Dimensions: {dim['width']}x{dim['height']}x{dim['depth']} {dim['unit']}"
            )
        
        # Add material if available
        material = product_info.get('material')
        if material:
            description_parts.append(f"Material: {material}")
        
        # Add color/finish if available
        color = product_info.get('color')
        if color:
            description_parts.append(f"Finish: {color}")
        
        # Add default description if none provided
        if len(description_parts) < 2:
            description_parts.append("High-quality kitchen and home organization solution.")
        
        return '\n'.join(description_parts)

    def clear_existing_data(self):
        """Clear existing product data."""
        self.stdout.write("Clearing existing product data...")
        
        # Get counts before deletion
        product_count = Product.objects.count()
        
        # Delete all products (this will cascade to product images)
        Product.objects.all().delete()
        
        # Clear media directory of product images
        media_root = settings.MEDIA_ROOT
        product_images_dir = os.path.join(media_root, 'product_images')
        if os.path.exists(product_images_dir):
            for filename in os.listdir(product_images_dir):
                file_path = os.path.join(product_images_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error deleting {file_path}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(
            f"Cleared {product_count} products and cleaned product_images directory"
        ))

    def ensure_category_structure(self):
        """Ensure the basic category structure exists."""
        self.stdout.write("Setting up category structure...")
        
        # Main categories
        main_categories = [
            'Storage Solutions',
            'Organization',
            'Hardware',
            'Furniture',
            'Kitchen Solutions'
        ]
        
        # Subcategories mapping
        subcategories = {
            'Storage Solutions': [
                'Baskets', 'Pullouts', 'Corner Units', 'Pantry Units',
                'Shelving', 'Racks', 'Bins', 'Metal Storage',
                'Wooden Storage', 'Plastic Storage', 'Custom Storage'
            ],
            'Organization': [
                'Drawer Systems', 'Trays', 'Organizers'
            ],
            'Hardware': [
                'Handles & Knobs', 'Hinges', 'Brackets & Supports',
                'Connectors', 'Profiles', 'Slides & Rails',
                'Rolling Shutters', 'General Hardware'
            ],
            'Furniture': [
                'Cabinets', 'Wardrobes', 'Shelving Units'
            ],
            'Kitchen Solutions': [
                'General Storage', 'Pantry Solutions', 'Corner Solutions'
            ]
        }
        
        # Create main categories
        for main_cat in main_categories:
            category, created = Category.objects.get_or_create(
                name=main_cat,
                defaults={'parent': None}
            )
            if created:
                self.stdout.write(f"Created main category: {main_cat}")
            
            # Create subcategories
            for sub_cat in subcategories.get(main_cat, []):
                sub_category, sub_created = Category.objects.get_or_create(
                    name=sub_cat,
                    defaults={'parent': category}
                )
                if sub_created:
                    self.stdout.write(f"Created subcategory: {sub_cat} under {main_cat}")
        
        self.stdout.write(self.style.SUCCESS("Category structure setup complete"))
