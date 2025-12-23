# your_project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import task_prerun, task_postrun
from django.db import close_old_connections

# set default Django settings module for 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_service.settings')

app = Celery('image_service')

# Close old DB connections before and after each task
@task_prerun.connect
def close_db_connections_before_task(**kwargs):
    close_old_connections()
    
@task_postrun.connect
def close_db_connections_after_task(**kwargs):
    close_old_connections()    

# Using a string here means the worker doesn’t have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()