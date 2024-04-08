from celery import shared_task
from django.core.mail import send_mail
from .models import CustomUser
from datetime import date

@shared_task
def check_user_activity():
    users = CustomUser.objects.all()
    for user in users:
        if not user.activityevent_set.filter(activity_date=date.today()).exists():
            send_mail(
                'Your Daily Activities',
                'Hello {}!'.format(user.username) + " We've noticed thar haven\'t added any activities today. "
                                                    "Remember to add them so stay on track!",
                'marc.saczek@gmail.com',
                [user.email],
                fail_silently=False,
            )