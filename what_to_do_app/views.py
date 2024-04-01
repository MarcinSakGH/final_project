from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, View, ListView, DeleteView, UpdateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, date
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
    def get(self, request, *args, **kwargs):
        form = ActivityEventForm()
        activities = ActivityEvent.objects.filter(user=self.request.user, activity_date=timezone.now()).order_by(
            '-activity_date')
        today = date.today()
        current_day_of_week = today.strftime("%A")
        ctx = {"form": form, 'current_day_of_week': current_day_of_week, "activities": activities,
               'today': today}
        return render(request, 'currentDayView.html', context=ctx)
    def post(self, request, *args, **kwargs):
        current_day_of_week = date.today().weekday()
        form = ActivityEventForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()
            return HttpResponseRedirect(reverse_lazy('current_day'))
