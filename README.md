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
- Users, profiles, addresses
- Products, categories, images, reviews, search & filtering
- Cart + order flow
- Stripe payments + webhook
- Caching, pagination, async email
- Swagger/ReDoc docs

## Quick Start
1) Create .env (see sample keys below)
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

## Docs & Admin
- Swagger: http://localhost:8000/api/schema/swagger-ui/
- ReDoc: http://localhost:8000/api/schema/redoc/
- Admin: http://localhost:8000/admin/

## Docker
- Build: docker-compose build
- Run: docker-compose up -d



