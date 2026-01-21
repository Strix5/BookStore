from config.settings.base import *


ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
