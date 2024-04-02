from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, View, ListView, DeleteView, UpdateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, date, timedelta
from .forms import CustomUserCreationForm, CustomUserChangeForm, ActivityForm, ActivityEventForm
from .models import Activity, ActivityEvent


# Create your views here.

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class CustomUserUpdateView(UpdateView):
    form_class = CustomUserChangeForm
    template_name = 'user_update.html'
    success_url = reverse_lazy('home')
    def get_object(self, queryset=None):
        return self.request.user


class ActivityListView(LoginRequiredMixin, ListView):
    model = Activity
    template_name = 'activity_list.html'

class ActivityCreateView(LoginRequiredMixin, CreateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'activity_form.html'
    success_url = reverse_lazy('activity_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ActivityUpdateView(LoginRequiredMixin, UpdateView):


    model = Activity
    form_class = ActivityForm
    template_name = 'activity_form.html'
    success_url = reverse_lazy('activity_list')


class ActivityDeleteView(LoginRequiredMixin, DeleteView):
    model = Activity
    template_name = 'activity_confirm_delete.html'
    success_url = reverse_lazy('activity_list')




class DayView(LoginRequiredMixin, View):
    def get(self, request, date=None):
        if date:
            current_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            current_date = datetime.now().date()
        form = ActivityEventForm()
        previous_day = current_date - timedelta(days=1)
        next_day = current_date + timedelta(days=1)
        activities = ActivityEvent.objects.filter(
            user=self.request.user,
            activity_date=current_date
        ).order_by('-activity_date')
        current_day_of_week = current_date.strftime("%A")
        ctx = {
            "form": form,
            "current_day_of_week": current_day_of_week,
            "activities": activities,
            "today": current_date,
            'previous_day': previous_day,
            "next_day": next_day
        }
        return render(request, 'dayView.html', context=ctx)

    def post(self, request, date, *args, **kwargs):
        if date:
            current_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            current_date = datetime.now().date()
        form = ActivityEventForm(request.POST)
        if form.is_valid():
            duration_hours = form.cleaned_data.get('duration_hours', 0)
            duration_minutes = int(form.cleaned_data.get('duration_minutes', 0))

            if duration_hours is None and duration_minutes is None:
                duration = None
            else:
                duration_hours = duration_hours or 0
                duration_minutes = int(duration_minutes or 0)
                duration = timedelta(hours=duration_hours, minutes=duration_minutes)

            activity = form.save(commit=False)
            activity.duration = duration
            activity.user = request.user
            activity.activity_date = datetime.strptime(date, '%Y-%m-%d').date()
            activity.save()
            return redirect('day', date=current_date.strftime("%Y-%m-%d"))

def add_activity(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            # save activity to database
            activity = form.save()
            return redirect('current_day', day=activity.date)
    else:
        form = ActivityForm(initial={'date': date.today()})
    return render(request, 'activity_form.html', {'form': form})


class ActivityEventDeleteView(DeleteView):
    model = ActivityEvent
    template_name = 'activityevent_confirm_delete.html'

    def get_success_url(self):
        activity_date = self.object.activity_date
        return reverse('day', kwargs={'date': activity_date.strftime("%Y-%m-%d")})
