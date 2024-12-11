from django.core.management.base import BaseCommand
from products.models import Category
from django.db.models import Count
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Remove categories that have no products"

    def handle(self, *args, **options):
        removed_categories = []
        total_categories = Category.objects.count()

        # First pass: Remove leaf categories (categories with no children) that are empty
        while True:
            # Get leaf categories with no products
            empty_leaves = Category.objects.annotate(
                product_count=Count("products"), child_count=Count("children")
            ).filter(product_count=0, child_count=0)

            if not empty_leaves.exists():
                break

            for category in empty_leaves:
                self.stdout.write(f"Removing empty leaf category: {category.name}")
                if category.parent_id:
                    try:
                        parent = Category.objects.get(id=category.parent_id)
                        self.stdout.write(f"  Parent category: {parent.name}")
                    except Category.DoesNotExist:
                        pass
                removed_categories.append(category.name)
                category.delete()

        # Second pass: Remove any remaining empty categories (these would be parents with no children and no products)
        remaining_empty = Category.objects.annotate(
            product_count=Count("products"), child_count=Count("children")
        ).filter(product_count=0, child_count=0)

        for category in remaining_empty:
            self.stdout.write(f"Removing empty parent category: {category.name}")
            removed_categories.append(category.name)
            category.delete()

        # Get remaining categories count
        remaining_categories = Category.objects.count()

        # Print summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCategory cleanup complete!\n"
                f"Total categories before cleaning: {total_categories}\n"
                f"Categories removed: {len(removed_categories)}\n"
                f"Remaining categories: {remaining_categories}"
            )
        )

        if removed_categories:
            self.stdout.write("\nRemoved categories:")
            for category in removed_categories:
                self.stdout.write(f"- {category}")

        # Print remaining category structure
        self.stdout.write("\nRemaining category structure:")
        root_categories = (
            Category.objects.filter(parent=None)
            .annotate(product_count=Count("products"))
            .order_by("name")
        )

        for root in root_categories:
            self.stdout.write(f"\n{root.name} ({root.product_count} products)")
            children = (
                Category.objects.filter(parent=root)
                .annotate(product_count=Count("products"))
                .order_by("name")
            )
            for child in children:
                self.stdout.write(f"  └─ {child.name} ({child.product_count} products)")
