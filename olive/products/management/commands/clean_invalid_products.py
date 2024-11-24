from django.core.management.base import BaseCommand
from products.models import Product
import logging
import re

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Remove products that do not match our kitchen and home organization focus'

    def __init__(self):
        super().__init__()
        self.common_product_terms = {
            'mm', 'cm', 'kg', 'lbs', 'oz', 'ml', 'ltr', 'pcs', 'qty', 'min', 'max',
            'organizer', 'organiser', 'storage', 'container', 'rack', 'holder', 'shelf',
            'drawer', 'basket', 'bin', 'box', 'tray', 'cabinet', 'pantry', 'closet',
            'wardrobe', 'hanger', 'hook', 'divider', 'liner', 'mount', 'mounted',
            'stackable', 'adjustable', 'expandable', 'compartment', 'tier', 'premium',
            'deluxe', 'stainless', 'steel', 'plastic', 'wooden', 'bamboo', 'chrome',
            'metallic', 'acrylic'
        }

    def is_valid_product_name(self, name):
        """Check if product name makes sense."""
        # Remove common measurements and numbers
        name = re.sub(r'\d+(?:\.\d+)?(?:mm|cm|m|kg|g|pcs|pc|inch|")', '', name.lower())
        name = re.sub(r'\(.*?\)', '', name)  # Remove content in parentheses
        
        # Split into words and filter out empty strings
        words = [w.strip() for w in name.split() if w.strip()]
        
        if not words:
            return False
            
        # Check for random characters or very short words
        invalid_patterns = [
            r'^[a-z]$',  # Single letter
            r'^[^a-z]+$',  # No letters
            r'^[a-z][0-9]$',  # Letter followed by number
            r'^.*[^a-z0-9\s\-].*$'  # Contains special characters
        ]
        
        invalid_word_count = 0
        for word in words:
            if any(re.match(pattern, word) for pattern in invalid_patterns):
                invalid_word_count += 1
                
        # If more than 30% of words are invalid, reject the name
        return (invalid_word_count / len(words)) <= 0.3

    def is_valid_description(self, description):
        """Check if product description is valid and meaningful."""
        if not description:
            return True  # Empty descriptions are allowed
            
        # Remove measurements and numbers
        cleaned_desc = re.sub(r'\d+(?:\.\d+)?(?:mm|cm|m|kg|g|pcs|pc|inch|")', '', description.lower())
        
        # Split into words
        words = [w.strip() for w in cleaned_desc.split() if w.strip()]
        
        if not words:
            return False
            
        # Check for random characters or very short words
        invalid_patterns = [
            r'^[a-z]$',  # Single letter
            r'^[^a-z]+$',  # No letters
            r'^[a-z][0-9]$',  # Letter followed by number
            r'^.*[^a-z0-9\s\-].*$'  # Contains special characters
        ]
        
        invalid_word_count = 0
        for word in words:
            if any(re.match(pattern, word) for pattern in invalid_patterns):
                invalid_word_count += 1
                
        # If more than 40% of words are invalid, reject the description
        return (invalid_word_count / len(words)) <= 0.4

    def handle(self, *args, **options):
        # Keywords that indicate valid products
        valid_keywords = [
            'storage', 'organizer', 'organization', 'container', 'basket', 
            'shelf', 'rack', 'kitchen', 'pantry', 'cabinet', 'drawer', 
            'spice', 'sink', 'bathroom', 'vanity', 'counter', 'closet', 
            'wardrobe', 'living'
        ]

        # Keywords that indicate invalid products
        invalid_keywords = [
            'toy', 'game', 'electronics', 'clothing', 'shoe', 'book', 
            'jewelry', 'watch', 'phone', 'computer', 'tablet', 'camera',
            'tool', 'garden', 'outdoor', 'sport', 'exercise', 'beauty',
            'makeup', 'pet', 'food', 'drink', 'grocery'
        ]

        total_products = Product.objects.count()
        removed_products = []

        # Check each product
        for product in Product.objects.all():
            name_lower = product.name.lower()
            desc_lower = product.description.lower() if product.description else ''

            # Check if product contains invalid keywords
            has_invalid = any(keyword in name_lower or keyword in desc_lower 
                            for keyword in invalid_keywords)

            # Check if product contains any valid keywords
            has_valid = any(keyword in name_lower or keyword in desc_lower 
                          for keyword in valid_keywords)

            # Check if name and description are valid
            name_valid = self.is_valid_product_name(product.name)
            desc_valid = self.is_valid_description(product.description)

            # Remove product if it fails any check
            if has_invalid or not has_valid or not name_valid or not desc_valid:
                removed_products.append(f"{product.name} (ID: {product.id})")
                product.delete()
                self.stdout.write(f"Removed invalid product: {product.name}")
                if not name_valid:
                    self.stdout.write(f"  Reason: Invalid product name")
                if not desc_valid:
                    self.stdout.write(f"  Reason: Invalid description")
                if has_invalid:
                    self.stdout.write(f"  Reason: Contains invalid keywords")
                if not has_valid:
                    self.stdout.write(f"  Reason: Missing valid keywords")

        # Print summary
        self.stdout.write(self.style.SUCCESS(
            f"\nCleaning complete!\n"
            f"Total products before cleaning: {total_products}\n"
            f"Products removed: {len(removed_products)}\n"
            f"Remaining products: {Product.objects.count()}"
        ))

        if removed_products:
            self.stdout.write("\nRemoved products:")
            for product in removed_products:
                self.stdout.write(f"- {product}")
