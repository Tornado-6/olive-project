# Django E-commerce Project

A modern e-commerce web application built with Django, featuring a responsive design and comprehensive shopping functionality.

## Features

- Product browsing and searching
- Shopping cart management
- User authentication and profiles
- Wishlist functionality
- Order processing
- Admin interface for product management

## Tech Stack

- Django 5.1.3
- Django REST Framework
- Bootstrap 5
- SQLite Database
- WhiteNoise for static files

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Tornado-6/django-ecommerce.git
cd django-ecommerce
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

- `products/`: Product management app
- `cart/`: Shopping cart functionality
- `orders/`: Order processing
- `users/`: User authentication and profiles

## Contributing

Feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License.
