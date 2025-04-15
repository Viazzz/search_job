from .base import *

SECRET_KEY = "django-insecure-*4p_b(kt)c5v$i@b97u2za@!@odo)rkhk9$t9t*d!_*z^gm)hz"

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static/'
]

INTERNAL_IPS = [
    "127.0.0.1",
]

### CACHES #######################
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
#         "LOCATION": "127.0.0.1:11211",
#     }
# }

# CACHE_MIDDLEWARE_SECONDS = 60