import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("bookstore")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()  # auto find tasks.py in all Django apps
