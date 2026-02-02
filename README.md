# E-Com API

Django REST Framework e-commerce backend with products, carts, orders, payments (Stripe), and JWT auth.

## Tech Stack
- Django 6.0.1, DRF 3.16.1
- PostgreSQL (prod) / SQLite (dev)
- Redis + Celery
- Stripe
- Docker + Gunicorn
- drf-spectacular (OpenAPI)

## Key Features
- User accounts with profiles and multiple addresses
- Product catalog with categories, images, reviews, search, and filters
- Cart management with quantity updates and totals
- Orders with billing/shipping info and status tracking
- Stripe payments with webhook confirmation
- Performance: caching, pagination, async email tasks
- API docs via Swagger/ReDoc

## Quick Start
1) Create .env 
2) Install deps: pip install -r requirements.txt
3) Migrate: python manage.py migrate
4) Run: python manage.py runserver

## Sample .env Keys
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
SECRET_KEY=your-secret
PUBLISHABLE_KEY=pk_test...
SECRET_KEY_STRIPE=sk_test...
STRIPE_WEBHOOK_SECRET=whsec...
CELERY_BROKER_URL=redis://localhost:6379/1
REDIS_BACKEND=redis://localhost:6379/2

## Docker
- Build: docker-compose build
- Run: docker-compose up -d



