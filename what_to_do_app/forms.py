from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models import Prefetch
from datetime import datetime, date, timedelta

from .models import CustomUser, Activity, ActivityEvent, UserActivityEmotion, Emotion, EmotionCategory


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = UserCreationForm.Meta.fields


class CustomUserChangeForm(UserChangeForm):
    password = None
    class Meta(UserChangeForm):
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class ActivityEventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['activity'].queryset = Activity.objects.filter(user=user)

    activity_date = forms.DateField(
        widget=forms.widgets.HiddenInput(),
        initial=datetime.today().strftime('%Y-%m-%d')
    )
    activity_time = forms.TimeField(
        input_formats=['%H:%M',  '%H:%M:%S'],
        widget=forms.widgets.TimeInput(attrs={'type': 'time', 'format': '%H:%M'}),

    )
    duration_hours = forms.IntegerField(min_value=0, required=False)
    duration_minutes = forms.ChoiceField(choices=[(i, f'{i} minutes') for i in range(0, 60, 15)], required=False)
    class Meta:
        model = ActivityEvent
        fields = ['activity', 'activity_date', 'activity_time',  'comment']

    def clean(self):
        cleaned_data = super().clean()

        hours = cleaned_data.get('duration_hours')
        minutes = cleaned_data.get('duration_minutes')

        if hours is None and minutes is None:
            cleaned_data['duration'] = None
        else:
            hours = hours or 0
            minutes = int(minutes) or 0
            cleaned_data['duration'] = timedelta(hours=hours, minutes=minutes)

        return cleaned_data

    def save(self, commit=True):
        instance = super(ActivityEventForm, self).save(commit=False)
        instance.duration = self.cleaned_data['duration']
        if commit:
            instance.save()
        return instance


def get_emotion_choices():
    categories = EmotionCategory.objects.all().prefetch_related(
        Prefetch(
            'emotions',
            queryset=Emotion.objects.all().only('name'),
            to_attr='emotions_list'
        )
    )

    is_grouped_choices = []

    for category in categories:
        emotion_choices = [(emotion.id, emotion.name) for emotion in category.emotions_list]
        is_grouped_choices.append((category.name, emotion_choices))

    return is_grouped_choices

class UserActivityEmotionForm(forms.ModelForm):
    intensity = forms.ChoiceField(choices=[(i, i) for i in range(1, 11)])
    class Meta:
        model = UserActivityEmotion
        fields = ['emotion', 'intensity', 'note', 'state']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['emotion'].choices = get_emotion_choices()

    def save(self, activityevent=None, commit=True):
        # This method overrides the native form's save method
        instance = super(UserActivityEmotionForm, self).save(commit=False)
        if activityevent:
            instance.activityevent = activityevent
        if commit:
            instance.save()
        return instance

class DaySelectionForm(forms.Form):
    date = forms.DateField()