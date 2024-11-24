# Olive Store

A modern e-commerce platform built with Django for Olive, featuring a responsive design and comprehensive product management system.

## Features

- Product catalog with categories
- User authentication and profiles
- Shopping cart functionality
- Wishlist management
- Order processing
- Product reviews and ratings
- Responsive design with Bootstrap 5
- RESTful API endpoints

## Tech Stack

- Django 5.1.3
- Python 3.8+
- Bootstrap 5
- SQLite (Development)
- Django REST Framework
- WhiteNoise
- django-cors-headers

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/olive-project.git
cd olive-project
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to see the application.

## Project Structure

```
olive/
├── manage.py
├── olive/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/
├── cart/
├── orders/
├── users/
└── media/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
