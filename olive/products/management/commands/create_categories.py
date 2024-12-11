from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = "Create initial product categories"

    def handle(self, *args, **options):
        # Main categories and their subcategories
        categories = {
            "Storage Solutions": [
                "Baskets",
                "Pullouts",
                "Corner Units",
                "Pantry Units",
                "Shelving",
                "Racks",
                "Bins",
                "Metal Storage",
                "Wooden Storage",
                "Plastic Storage",
                "Custom Storage",
                "Wicker Baskets",
            ],
            "Organization": ["Drawer Systems", "Trays"],
            "Hardware": [
                "General Hardware",
                "Handles & Knobs",
                "Hinges",
                "Brackets & Supports",
                "Connectors",
                "Profiles",
                "Slides & Rails",
                "Rolling Shutters",
            ],
            "Furniture": ["Cabinets"],
            "Kitchen Solutions": ["General Storage"],
        }

        # Create categories
        for main_category, subcategories in categories.items():
            main_cat, created = Category.objects.get_or_create(
                name=main_category,
                defaults={"slug": main_category.lower().replace(" ", "-")},
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created main category: {main_category}")
                )

            for subcategory in subcategories:
                sub_cat, created = Category.objects.get_or_create(
                    name=subcategory,
                    parent=main_cat,
                    defaults={"slug": subcategory.lower().replace(" ", "-")},
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created subcategory: {subcategory} under {main_category}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("Successfully created all categories"))
