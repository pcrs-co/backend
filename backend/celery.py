# backend/celery.py

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
# This line is crucial for Celery to know about your Django project settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Create the Celery application instance.
# 'backend' is the name of your main Django project.
app = Celery("backend")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix in settings.py.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
# Celery will automatically look for a 'tasks.py' file in each app.
app.autodiscover_tasks()
