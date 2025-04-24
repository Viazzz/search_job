import os

from celery import Celery

from django.conf import settings

# this code copied from manage.py
# set the default Django settings module for the 'celery' app.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.variables.prod')

# you can change the name here
app = Celery("django_celery")
app.conf.update(
    timezone='Europe/Moscow', 
    enable_utc=True,
    worker_hijack_root_logger=False,
)

# read config from Django settings, the CELERY namespace would make celery
# config keys has `CELERY` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# discover and load tasks.py from from all registered Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
