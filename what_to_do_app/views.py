from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, View, ListView, DeleteView, UpdateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, date, timedelta
from .forms import CustomUserCreationForm, CustomUserChangeForm, ActivityForm, ActivityEventForm
from .models import Activity, ActivityEvent
from django.contrib.auth.decorators import login_required


# Create your views here.

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class CustomLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        request.session['login_attempts'] = 0
        return super().get(request, *args, **kwargs)
    def form_valid(self, form):
        """If form is valid redirect to the supplied URL"""
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """If form is invalid, render the invalid form"""
        if 'login_attempts' in self.request.session:
            self.request.session['login_attempts'] += 1
        else:
            self.request.session['login_attempts'] = 1
        return self.render_to_response(self.get_context_data(form=form))

class CustomUserUpdateView(UpdateView):
    form_class = CustomUserChangeForm
    template_name = 'user_update.html'
    success_url = reverse_lazy('home')
    def get_object(self, queryset=None):
        return self.request.user


class ActivityListView(LoginRequiredMixin, ListView):
    model = Activity
    template_name = 'activity_list.html'

    def get_queryset(self):
        # Ogranicz zwracany queryset do aktywności bieżącego użytkownika
        return Activity.objects.filter(user=self.request.user)

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
        form = ActivityEventForm(user=request.user)
        previous_day = current_date - timedelta(days=1)
        next_day = current_date + timedelta(days=1)
        print(self.request.user, self.request.user.id)
        activities = ActivityEvent.objects.filter(
            user=self.request.user,
            activity_date=current_date
        ).order_by('-activity_date')
        print(activities)
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

    def post(self, request, date=None, *args, **kwargs):
        if date:
            current_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            current_date = datetime.now().date()
        form = ActivityEventForm(request.POST, user=request.user)
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
            activity.activity_date = current_date
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


@login_required
def show_user(request):
    return HttpResponse(f'Zalogowany użytkownik: {request.user.username}')