import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Set the default queue
app.conf.task_default_queue = 'default'

# Configure the task serializer, result serializer and accept content
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# Configure timezone
app.conf.timezone = 'UTC'
app.conf.enable_utc = True

# Worker settings
app.conf.worker_max_tasks_per_child = 100
app.conf.worker_prefetch_multiplier = 1

# Windows-specific settings
if os.name == 'nt':
    # Use solo pool for Windows compatibility
    app.conf.worker_pool = 'solo'

