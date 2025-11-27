import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "ats.sqlite3",
    }
}


# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
MEDIA_URL = "/images/"

STATIC_ROOT = BASE_DIR / "assets"
MEDIA_ROOT =  BASE_DIR / "static/images"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
