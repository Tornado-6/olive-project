from rest_framework import serializers
from .models import Product, Category, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "title", "comment", "created_at"]
        read_only_fields = ["user"]


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    images = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "category",
            "images",
            "image_url",
            "average_rating",
            "total_reviews",
            "reviews",
        ]

    def get_images(self, obj):
        if obj.image and hasattr(obj.image, "url"):
            return [obj.image.url]
        return []

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_average_rating(self, obj):
        return obj.average_rating

    def get_total_reviews(self, obj):
        return obj.total_reviews
