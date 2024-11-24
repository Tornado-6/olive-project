from django.core.management.base import BaseCommand
from products.models import Category

class Command(BaseCommand):
    help = 'Update category descriptions with detailed information'

    def handle(self, *args, **options):
        category_descriptions = {
            'Kitchen Solutions': 'Complete range of kitchen organization and storage solutions. From pullouts to baskets, find everything you need to create an efficient and organized kitchen space.',
            
            # Kitchen subcategories
            'Baskets': 'High-quality storage baskets designed for kitchen cabinets. Available in multiple series to match your needs and budget.',
            'Pullouts': 'Smooth-operating pullout systems for easy access to kitchen storage. Various sizes and configurations available.',
            'Storage Solutions': 'Specialized storage solutions for corner spaces and pantry organization. Maximize your kitchen storage efficiency.',
            'Drawer Systems': 'Premium drawer systems including Drawell Box and Slimtek options. Soft-close mechanisms and durable construction.',
            'Other Kitchen Items': 'Additional kitchen organization products including wicker baskets, rolling shutters, and essential hardware fittings.',
            
            # Specific product categories
            'Corner Units': 'Innovative solutions for corner cabinet storage. Make the most of corner spaces with accessible storage options.',
            'Pantry Units': 'Organized storage solutions for pantry spaces. Efficient systems for food and supply storage.',
            'Drawell Box': 'Premium drawer box system with modern features. Soft-close mechanism and sturdy construction.',
            'Slimtek Drawers': 'Sleek and space-efficient drawer systems. Modern design with smooth operation.',
            'Wicker Baskets': 'Natural wicker storage solutions. Blend of traditional style and practical storage.',
            'Rolling Shutters': 'Modern cabinet door solutions. Space-saving design with smooth operation.',
            'Hardware Fittings': 'Essential hardware components for kitchen installations. Quality fittings for various applications.',
            
            # Other main categories
            'Wardrobe Accessories': 'Complete range of wardrobe organization solutions. Maximize your closet space with our innovative storage systems.',
            'Bathroom Accessories': 'Modern bathroom storage and organization products. Enhance your bathroom functionality with our quality accessories.',
            'Door Systems': 'Advanced door solutions for various applications. Sliding systems and modern door hardware.',
        }

        # Series descriptions to be applied to both Baskets and Pullouts series
        series_descriptions = {
            'Platinum Series': 'Premium line featuring top-tier materials and advanced functionality. Best-in-class durability and elegant design.',
            'Signature Series': 'Exclusive collection combining style and functionality. Superior quality with distinctive design elements.',
            'Gold Series': 'High-end products offering excellent value. Premium features and reliable performance.',
            'Sparkle Series': 'Modern designs with contemporary aesthetics. Perfect blend of style and practicality.',
            'Silver Series': 'Quality products at competitive prices. Reliable performance and practical design.',
            'Pearl Series': 'Essential collection offering great value. Functional designs for everyday use.',
        }

        # Update main categories and subcategories
        for category_name, description in category_descriptions.items():
            categories = Category.objects.filter(name=category_name)
            for category in categories:
                category.description = description
                category.save()
                self.stdout.write(self.style.SUCCESS(f'Updated description for: {category.full_name}'))

        # Update series descriptions
        for series_name, description in series_descriptions.items():
            series_categories = Category.objects.filter(name=series_name)
            for category in series_categories:
                category.description = description
                category.save()
                self.stdout.write(self.style.SUCCESS(f'Updated description for: {category.full_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully updated all category descriptions'))
