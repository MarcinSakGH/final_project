from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from datetime import  timedelta
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'what_to_do.settings')
app = Celery('what_to_do')
app.conf.timezone = 'Europe/Warsaw'
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

CELERY_BEAT_SCHEDULE = {
    'check_user_activity': {
        'task': 'what_to_do_app.tasks.check_user_activity',
        'schedule': crontab(hour='18', minute='00')
    }
}

app.conf.beat_schedule = CELERY_BEAT_SCHEDULE


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))