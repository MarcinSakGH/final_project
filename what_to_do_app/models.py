from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username

class EmotionCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class EmotionType(models.Model):
    POSITIVE = 1
    NEGATIVE = -1
    WEIGHT_CHOICES = (
        (POSITIVE, 'Positive'),
        (NEGATIVE, 'Negative'),
    )
    name = models.CharField(max_length=255)
    weight = models.IntegerField(choices=WEIGHT_CHOICES)

    def __str__(self):
        return self.name


class Emotion(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(EmotionCategory, related_name='emotions', on_delete=models.CASCADE)
    emotion_type = models.ForeignKey(EmotionType, related_name='emotions', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.name


class Activity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def calculate_total_activity_score(self):
        total_activity_score = 0
        # get all ActivityEvents associated with this Activity
        activity_events = ActivityEvent.objects.filter(activity=self)

        # for every activityEvent count score and add to total_score
        for event in activity_events:
            total_activity_score += event.activity_score

        return total_activity_score

    def __str__(self):
        return self.name




class ActivityEvent(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    activity_date = models.DateField(null=True, blank=True)
    activity_time = models.TimeField(null=True, blank=True)
    duration = models.DurationField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    user_emotions = models.ManyToManyField(Emotion, through='UserActivityEmotion', related_name='emotions')
    activity_score = models.FloatField(default=0, blank=True, null=True)

    def calculate_activity_score(self):
        # wages for different emotion states
        state_weights = {'BEFORE': 0.2, 'DURING': 0.3, 'AFTER': 0.5}
        total_score = 0

        # get all emotions associated with this ActivityEvent
        user_activity_emotions = UserActivityEmotion.objects.filter(activityevent=self)

        # for every UserActivityEmotion count score and add to total_score
        for user_activity_emotion in user_activity_emotions:
            emotion_type_weight = user_activity_emotion.emotion.emotion_type.weight
            state_weight = state_weights[user_activity_emotion.state]
            score = user_activity_emotion.intensity * emotion_type_weight * state_weight
            total_score += score

        # update field activity_score for this ActivityEvent
        self.activity_score = total_score
        self.save()

    def __str__(self):
        return f'{self.user.username} - {self.activity.name} at {self.timestamp}'


class UserActivityEmotion(models.Model):
    STATE_CHOICES = [
        ('BEFORE', 'Before activity'),
        ('DURING', 'During activity'),
        ('AFTER', 'After activity')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    activityevent = models.ForeignKey(ActivityEvent, on_delete=models.CASCADE)
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE)
    intensity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    note = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES)

    def __str__(self):
        return f'{self.user} - {self.emotion.name}'

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)