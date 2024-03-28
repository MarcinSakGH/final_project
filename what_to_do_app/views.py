from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, View
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime

from .forms import CustomUserCreationForm, CustomUserChangeForm

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


class DayView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        current_day_of_week = datetime.date.today().weekday()
        ctx = {'current_day_of_week': current_day_of_week}
        return render(request, 'currentDayView.html', context=ctx)