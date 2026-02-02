FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (needed for psycopg2, Pillow, etc.)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends gcc libpq-dev \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip \
	&& pip install -r requirements.txt

# Project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "120"]
