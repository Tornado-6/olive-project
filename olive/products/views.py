from django.shortcuts import render, get_object_or_404, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Category, Review
from .serializers import ProductSerializer, ReviewSerializer
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Create your views here.

def home(request):
    logger.debug("Home view called with request: %s", request)
    logger.debug("Template dirs: %s", settings.TEMPLATES[0]['DIRS'])
    logger.debug("App dirs enabled: %s", settings.TEMPLATES[0]['APP_DIRS'])
    
    # Get all categories for sidebar
    categories = Category.objects.all()
    selected_category = None
    
    # Base queryset
    products = Product.objects.all()
    logger.debug("Found %d products", products.count())
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=selected_category)
    
    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=float(min_price))
    if max_price:
        products = products.filter(price__lte=float(max_price))
    
    # Sorting
    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')
    elif sort == 'rating_desc':
        products = sorted(products, key=lambda p: p.average_rating, reverse=True)
    
    # Pagination
    paginator = Paginator(products, 9)  # Show 9 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
    }
    
    try:
        response = render(request, 'products/home.html', context)
        logger.debug("Rendered template successfully")
        return response
    except Exception as e:
        logger.error("Error rendering template: %s", str(e))
        return HttpResponse(f"Error: {str(e)}")

def category_view(request, category_id):
    logger.debug("Category view called with category_id: %s", category_id)
    category = get_object_or_404(Category, id=category_id)
    return home(request)

@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail_api(request, product_id):
    """Get product details including reviews"""
    logger.debug("Product detail API called for product_id: %s", product_id)
    product = get_object_or_404(Product, id=product_id)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, product_id):
    """Add a review to a product"""
    logger.debug("Add review called for product_id: %s", product_id)
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user already reviewed this product
    if Review.objects.filter(product=product, user=request.user).exists():
        return Response(
            {'error': 'You have already reviewed this product'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_review(request, review_id):
    """Update or delete a review"""
    logger.debug("Manage review called for review_id: %s with method: %s", review_id, request.method)
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    serializer = ReviewSerializer(review, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def about(request):
    """About page view."""
    return render(request, 'products/about.html')

def contact(request):
    """Contact page view."""
    return render(request, 'products/contact.html')
