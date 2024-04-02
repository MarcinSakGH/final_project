from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from datetime import datetime, date, timedelta

from .models import CustomUser, Activity, ActivityEvent


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = UserCreationForm.Meta.fields


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = CustomUser
        fields = ['username','first_name', 'last_name', 'email']


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class ActivityEventForm(forms.ModelForm):
    activity_date = forms.DateField(
        widget=forms.widgets.HiddenInput(),
        initial=datetime.today().strftime('%Y-%m-%d')
    )
    activity_time = forms.TimeField(
        input_formats=['%H:%M'],
        widget=forms.widgets.TimeInput(attrs={'type': 'time'}),
        help_text='Format: 24-hour clock'
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
