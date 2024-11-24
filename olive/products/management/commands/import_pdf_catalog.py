import os
import pdfplumber
import tabula
from pdf2image import convert_from_path
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from products.models import Product, Category
from decimal import Decimal
import logging
import tempfile
from PIL import Image
import io

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import products from a PDF catalog'

    def add_arguments(self, parser):
        parser.add_argument('pdf_path', type=str, help='Path to the PDF catalog')
        parser.add_argument('--category', type=str, help='Category name for imported products')
        parser.add_argument('--default-stock', type=int, default=0, help='Default stock quantity')

    def extract_tables(self, pdf_path):
        """Extract tables from PDF using tabula-py"""
        try:
            # Extract all tables from the PDF
            tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            return tables
        except Exception as e:
            logger.error(f"Error extracting tables: {str(e)}")
            return []

    def extract_images(self, pdf_path):
        """Extract images from PDF pages"""
        try:
            # Convert PDF pages to images
            images = convert_from_path(pdf_path)
            return images
        except Exception as e:
            logger.error(f"Error extracting images: {str(e)}")
            return []

    def process_table_row(self, row, category):
        """Process a single row from the extracted table"""
        try:
            # Adjust these indices based on your PDF structure
            name = row.get('Product Name', row.get('Name', ''))
            price = row.get('Price', '0')
            description = row.get('Description', '')
            
            # Clean and validate data
            if not name:
                return None
            
            # Convert price to Decimal
            try:
                price = Decimal(str(price).replace('$', '').strip())
            except:
                price = Decimal('0')
            
            # Create or update product
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'description': description,
                    'price': price,
                    'category': category,
                    'stock': self.default_stock
                }
            )
            
            return product
        except Exception as e:
            logger.error(f"Error processing row: {str(e)}")
            return None

    def save_product_image(self, product, image):
        """Save an extracted image to a product"""
        try:
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # Save image to product
            image_name = f"{slugify(product.name)}.png"
            product.image.save(image_name, ContentFile(img_byte_arr), save=True)
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")

    def handle(self, *args, **options):
        pdf_path = options['pdf_path']
        category_name = options['category']
        self.default_stock = options['default_stock']

        if not os.path.exists(pdf_path):
            self.stderr.write(f"PDF file not found: {pdf_path}")
            return

        # Get or create category
        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={'slug': slugify(category_name)}
        )

        # Extract tables
        tables = self.extract_tables(pdf_path)
        if not tables:
            self.stderr.write("No tables found in PDF")
            return

        # Process each table
        products_created = 0
        for table in tables:
            # Convert table to dict format
            table_dict = table.to_dict('records')
            for row in table_dict:
                product = self.process_table_row(row, category)
                if product:
                    products_created += 1

        # Extract and process images
        images = self.extract_images(pdf_path)
        if images and products_created > 0:
            products = Product.objects.filter(category=category).order_by('created_at')
            for product, image in zip(products, images):
                self.save_product_image(product, image)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported {products_created} products into category "{category_name}"'
            )
        )
