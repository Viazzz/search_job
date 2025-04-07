from .base import *

import os


DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY")

ADMINS = [
  ('Molodtsov A', 'aleksandr.molodtsov@corphn.com')
]

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': os.environ.get('POSTGRES_DB'),
       'USER': os.environ.get('POSTGRES_USER'),
       'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
       'HOST': 'db',
       'PORT': 5432,
   }
}


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'