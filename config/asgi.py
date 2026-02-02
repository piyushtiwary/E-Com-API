"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from dotenv import load_dotenv
from pathlib import Path

from django.core.asgi import get_asgi_application

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv("DJANGO_SETTINGS_MODULE", "config.settings"))

application = get_asgi_application()
