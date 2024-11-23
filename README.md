# Django E-Commerce Platform

## Overview
A comprehensive e-commerce platform built with Django, offering robust features for online shopping.

## Key Features
- User Authentication & Profiles
- Product Catalog with Categories
- Shopping Cart Management
- Order Processing
- Secure Checkout
- Responsive Design

## Technology Stack
- Backend: Django 5.1.3
- Database: PostgreSQL
- Frontend: HTML, CSS, JavaScript
- Payment Integration: Stripe
- Authentication: Django Built-in + Custom User Model

## Setup Instructions

### Prerequisites
- Python 3.9+
- pip
- virtualenv

### Installation
1. Clone the repository
2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create Superuser
```bash
python manage.py createsuperuser
```

6. Run Development Server
```bash
python manage.py runserver
```

## Environment Variables
Create a `.env` file with:
- `SECRET_KEY`
- `DEBUG`
- `DATABASE_URL`
- `STRIPE_SECRET_KEY`

## Deployment
- Configured for Heroku/Railway
- Uses `gunicorn` and `whitenoise`

## Contributing
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push and create Pull Request

## License
MIT License
