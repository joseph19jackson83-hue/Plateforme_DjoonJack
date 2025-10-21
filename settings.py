import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJ_SECRET', 'change-this-secret-in-prod')
DEBUG = os.getenv('DJ_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('DJ_ALLOWED_HOSTS','*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'core','rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'djoonjack_site.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'core' / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors':[
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]}
}]

WSGI_APPLICATION = 'djoonjack_site.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'America/Port-au-Prince'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # PythonAnywhere: collectstatic -> staticfiles

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# MonCash env (put on PythonAnywhere web UI env vars)
MONCASH_API_BASE = os.getenv('MONCASH_API_BASE','')
MONCASH_CLIENT_ID = os.getenv('MONCASH_CLIENT_ID','')
MONCASH_CLIENT_SECRET = os.getenv('MONCASH_CLIENT_SECRET','')
MONCASH_WEBHOOK_SECRET = os.getenv('MONCASH_WEBHOOK_SECRET','')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL','admin@djoonjack.local') 