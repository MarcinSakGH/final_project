web: python manage.py runserver
worker: celery -A what_to_do worker --loglevel=info
beat: celery -A what_to_do beat --loglevel=info