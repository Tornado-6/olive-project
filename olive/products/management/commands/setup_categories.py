from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = "Sets up initial product categories based on the catalog structure"

    def handle(self, *args, **options):
        # Main product categories
        main_categories = [
            "Kitchen Solutions",
            "Wardrobe Accessories",
            "Bathroom Accessories",
            "Door Systems",
        ]

        # Kitchen subcategories with their series
        kitchen_subcategories = {
            "Baskets": [
                "Platinum Series",
                "Signature Series",
                "Gold Series",
                "Sparkle Series",
                "Silver Series",
                "Pearl Series",
            ],
            "Pullouts": [
                "Platinum Series",
                "Signature Series",
                "Gold Series",
                "Sparkle Series",
                "Silver Series",
                "Pearl Series",
            ],
            "Storage Solutions": [
                "Corner Units",
                "Pantry Units",
            ],
            "Drawer Systems": [
                "Drawell Box",
                "Slimtek Drawers",
            ],
            "Other Kitchen Items": [
                "Wicker Baskets",
                "Rolling Shutters",
                "Hardware Fittings",
            ],
        }

        # Create main categories
        for category_name in main_categories:
            category, created = Category.objects.get_or_create(name=category_name)
            status = "Created" if created else "Already exists"
            self.stdout.write(f"{status}: {category_name}")

            # Add subcategories for Kitchen Solutions
            if category_name == "Kitchen Solutions":
                for subcategory_name, series_list in kitchen_subcategories.items():
                    subcategory, created = Category.objects.get_or_create(
                        name=subcategory_name, parent=category
                    )
                    status = "Created" if created else "Already exists"
                    self.stdout.write(f"  {status}: {subcategory_name}")

                    # Add series as sub-subcategories
                    for series_name in series_list:
                        series, created = Category.objects.get_or_create(
                            name=series_name, parent=subcategory
                        )
                        status = "Created" if created else "Already exists"
                        self.stdout.write(f"    {status}: {series_name}")

        self.stdout.write(self.style.SUCCESS("Successfully set up all categories"))
