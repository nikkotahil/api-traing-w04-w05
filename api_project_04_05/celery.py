import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_project_04_05.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()