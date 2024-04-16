# Standard library imports
from collections import defaultdict
from datetime import datetime, date, timedelta


# Django related imports
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Prefetch
from django.utils import timezone
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView, View, ListView, DeleteView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage

# Local application/library specific imports.
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    ActivityForm,
    ActivityEventForm,
    UserActivityEmotionForm
)
from .models import Activity, ActivityEvent, UserActivityEmotion
from .utils import generate_summary


# Create your views here.

class SignUpView(CreateView):
    """
    SignUpView

    This class is a view for handling user sign up functionality.

    Attributes:
        form_class (Form): The form class used for user sign up.
        success_url (str): The URL to redirect to after successful user sign up.
        template_name (str): The name of the template to render for user sign up.

    """
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class CustomLoginView(LoginView):
    """
    CustomLoginView

    This class extends the LoginView class and provides custom implementation for the login view.

    Methods:
        - get(self, request, *args, **kwargs):
            Sets 'login_attempts' session variable to 0 and calls the parent's get method.

        - form_valid(self, form):
            If the form is valid, logs in the user and redirects to the success URL.

        - form_invalid(self, form):
            If the form is invalid, increments the 'login_attempts' session variable and renders the invalid form.

    """
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
    """
    A class-based view for updating a custom user's information.

    Inherits from the UpdateView class provided by Django.

    Attributes:
        form_class (Form): The form class used for updating the user's information.
        template_name (str): The name of the template to be used for rendering the update view.
        success_url (str): The URL to redirect to after a successful update.

    Methods:
        get_object(queryset=None): Returns the user object for the current request.

    Example Usage:
        view = CustomUserUpdateView.as_view()
    """
    form_class = CustomUserChangeForm
    template_name = 'user_update.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user


class ActivityListView(LoginRequiredMixin, ListView):
    """ActivityListView class

    This class is responsible for displaying a list of activities for the logged-in user.

    Attributes:
        model: The model class representing the activity data.
        template_name: The name of the template to be used for rendering the activity list page.
        context_object_name: The name to be used for the activity list in the template context.

    Methods:
        get_queryset(): Returns the queryset of activities for the current user.
        get_context_data(**kwargs): Adds additional context data to the template context.

    """
    model = Activity
    template_name = 'activity_list.html'
    context_object_name = 'activities'

    def get_queryset(self):
        # Ogranicz zwracany queryset do aktywności bieżącego użytkownika
        return Activity.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities_with_score = []
        for activity in context['activities']:
            total_score = activity.calculate_total_activity_score()
            activities_with_score.append(
                {
                    'activity': activity,
                    'total_score': total_score if total_score else 0
                }
            )
        activities_with_score.sort(key=lambda x: x['total_score'], reverse=True)
        context['activities'] = activities_with_score
        return context


class ActivityCreateView(LoginRequiredMixin, CreateView):
    """
    A class representing the Create View for the Activity model.

    This view allows users to create new instances of Activity by filling in a form.
    The user must be logged in to access this view.

    Attributes:
        model (Activity): The model class that this view creates instances of.
        form_class (ActivityForm): The form class to use for creating instances of Activity.
        template_name (str): The name of the template to use for rendering the form.
        success_url (str): The URL to redirect to after successful form submission.

    Methods:
        form_valid(form): Called when a valid form is submitted. Saves the current user as the creator of the Activity.

    """
    model = Activity
    form_class = ActivityForm
    template_name = 'activity_form.html'
    success_url = reverse_lazy('activity_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ActivityUpdateView(LoginRequiredMixin, UpdateView):
    """

    ActivityUpdateView

    This class is a view that handles updating an existing activity.

    Attributes:
        model (class): The model class for the activity.
        form_class (class): The form class for the activity.
        template_name (str): The name of the template to be used for rendering the form.
        success_url (str): The URL to redirect to after a successful update.

    """
    model = Activity
    form_class = ActivityForm
    template_name = 'activity_form.html'
    success_url = reverse_lazy('activity_list')


class ActivityDeleteView(LoginRequiredMixin, DeleteView):
    """
    This class is a view used to delete an Activity object.

    Attributes:
        model: The model class which the view is associated with (Activity).
        template_name: The name of the template to be used for rendering the delete confirmation page
        ('activity_confirm_delete.html').
        success_url: The URL to redirect to after successful deletion of the Activity object ('activity_list').

    """
    model = Activity
    template_name = 'activity_confirm_delete.html'
    success_url = reverse_lazy('activity_list')


class DayView(LoginRequiredMixin, View):
    """
    The `DayView` class handles the rendering of a day view page and the processing of form submissions.

    Attributes:
        - activity_event_form (ActivityEventForm): An instance of the ActivityEventForm class.
        - user_activity_emotion_form (UserActivityEmotionForm): An instance of the UserActivityEmotionForm class.

    Methods:
        - day_status(day): Returns a string indicating the status of the given day (Today, Tomorrow, Yesterday).
        - get(request, date=None): Handles GET requests for the day view page. If a date is provided, it sets the
        current date to the specified date, otherwise it uses the current date.
    * It creates instances of the activity event and user activity emotion forms, retrieves the activities for the
    current date, and prepares the context for rendering the template. If the
    * 'request_summary' parameter is present in the request query params, it generates a summary of the activities and
    stores it in the session. If a summary already exists in the session
    *, it retrieves it and adds it to the context. It then renders the day view template with the context.
        - post(request, date=None, *args, **kwargs): Handles POST requests for the day view page. If a date is provided,
         it sets the current date to the specified date, otherwise it uses
    * the current date. It validates the submitted activity event form and, if valid, saves the activity event with
     the specified duration, user, and date. It also saves the user activity
    * emotion form for the user. It then redirects to the day view page for the current date.

    Note: This class requires the LoginRequiredMixin and View classes.
    """
    def day_status(self, day):
        today = datetime.today().date()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        if day == today:
            return 'Today'
        if day == tomorrow:
            return 'Tomorrow'
        if day == yesterday:
            return 'Yesterday'

    def get(self, request, date=None):
        if date:
            current_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            current_date = datetime.now().date()
        activity_event_form = ActivityEventForm(user=request.user)
        user_activity_emotion_form = UserActivityEmotionForm(prefix='uae')
        previous_day = current_date - timedelta(days=1)
        next_day = current_date + timedelta(days=1)
        # print(self.request.user, self.request.user.id)

        user_activity_emotion_prefetch = Prefetch('useractivityemotion_set',
                                                  queryset=UserActivityEmotion.objects.filter(
                                                      user=self.request.user))
        activities = ActivityEvent.objects.filter(
            user=self.request.user,
            activity_date=current_date
        ).prefetch_related(user_activity_emotion_prefetch).order_by('-activity_date')
        current_day_of_week = current_date.strftime("%A")
        current_day_status = self.day_status(current_date)
        ctx = {
            "activity_event_form": activity_event_form,
            "user_activity_emotion_form": user_activity_emotion_form,
            "current_day_of_week": current_day_of_week,
            "activities": activities,
            "today": current_date,
            'previous_day': previous_day,
            "next_day": next_day,
            'current_day_status': current_day_status,
        }

        summary_key = f'summary_{current_date}'
        if 'request_summary' in request.GET:
            activities_info = []
            for activity in activities:
                # for every activity get description, duration, comments and associated emotions
                descriptions = activity.activity.description
                durations = str(activity.duration)
                comments = activity.comment
                # get names of emotions associated with every activity
                emotions = ", ".join([emotion.name for emotion in activity.user_emotions.all()])

                # format all info as string and add them to the list
                activity_info = (f"During the activity of {activity.activity.name}, which lasted for {durations}, "
                                 f"the following emotions were experienced: {emotions}. "
                                 f"The activity had the following description: {descriptions}.")
                activities_info.append(activity_info)

            data_to_summarize = " ".join(activities_info)  # join all information in one string
            print('Data to be summarized:', data_to_summarize)
            # check if the summary exists in the session. If it doesn't - create a new one
            summary = request.session.get(summary_key)
            if not summary:
                summary = generate_summary(data_to_summarize)
                request.session[summary_key] = summary
            ctx['summary'] = summary
        else:
            summary = request.session.get(summary_key)  # retrieve from session
            if summary:
                ctx['summary'] = summary

        return render(request, 'dayView.html', context=ctx)

    def post(self, request, date=None, *args, **kwargs):
        if date:
            current_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            current_date = datetime.now().date()
        activity_event_form = ActivityEventForm(request.POST, user=request.user)
        if activity_event_form.is_valid():
            duration_hours = activity_event_form.cleaned_data.get('duration_hours', 0)
            duration_minutes = int(activity_event_form.cleaned_data.get('duration_minutes', 0))

            if duration_hours is None and duration_minutes is None:
                duration = None
            else:
                duration_hours = duration_hours or 0
                duration_minutes = int(duration_minutes or 0)
                duration = timedelta(hours=duration_hours, minutes=duration_minutes)

            activity = activity_event_form.save(commit=False)
            activity.duration = duration
            activity.user = request.user
            activity.activity_date = current_date
            activity.save()

            user_activity_emotion_form = UserActivityEmotionForm(request.POST, prefix='uae')
            if user_activity_emotion_form.is_valid():
                user_activity_emotion = user_activity_emotion_form.save(commit=False)
                user_activity_emotion.user = request.user
                user_activity_emotion.save()

            return redirect('day', date=current_date.strftime("%Y-%m-%d"))


def add_activity(request):
    """
    Add an activity to the database.

    Parameters:
    - request: HttpRequest object representing the incoming request

    Returns:
    - HttpResponseRedirect: Redirects to the 'current_day' view if the request method is POST and the form is valid.
    - HttpResponse: Renders the 'activity_form.html' template if the request method is not POST.

    """
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            # save activity to database
            activity = form.save()
            return redirect('current_day', day=activity.date)
    else:
        form = ActivityForm(initial={'date': date.today()})
    return render(request, 'activity_form.html', {'form': form})


class ActivityEventUpdateView(LoginRequiredMixin, UpdateView):
    """
    ActivityEventUpdateView class

    This class is a view for updating activity events. It is a subclass of the LoginRequiredMixin and UpdateView classes.

    Attributes:
    - model: The model associated with this view, which is ActivityEvent.
    - form_class: The form class used for updating activity events, which is ActivityEventForm.
    - template_name: The template used for rendering the update view, which is 'activity_event_edit.html'.

    Methods:
    - get_success_url(): Returns the URL to redirect to after successfully updating an activity event.
    It retrieves the activity_date attribute of the updated activity event and uses it
    * to construct the URL by calling the reverse() function with the 'day' view and the activity date as parameters.
    - get_form_kwargs(): Returns the keyword arguments to use when instantiating the form class. It first calls the
    get_form_kwargs() method of the parent class to get the initial kwargs
    *, then adds the 'user' attribute with the current user from the request.
    - get_initial(): Returns the initial data for the form. It first calls the get_initial() method of the parent class
    to get the initial data, then adds the 'duration_hours' and 'duration
    *_minutes' attributes based on the duration of the activity event converted into hours and minutes.

    Note: This class requires the LoginRequiredMixin mixin to ensure that only logged-in users can access the view.
    """
    model = ActivityEvent
    form_class = ActivityEventForm
    template_name = 'activity_event_edit.html'

    def get_success_url(self):
        activity_date = self.object.activity_date
        return reverse('day', kwargs={'date': activity_date.strftime("%Y-%m-%d")})

    def get_form_kwargs(self):
        # get the current form kwargs
        kwargs = super().get_form_kwargs()
        # update the kwargs with the user_id
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()

        # Get the current duration
        duration = self.object.duration

        if duration:
            # Convert duration into hours and minutes
            initial['duration_hours'], rem = divmod(duration.seconds, 3600)
            initial['duration_minutes'] = rem // 60

        return initial


class ActivityEventDeleteView(DeleteView):
    """
    Class ActivityEventDeleteView represents a view for deleting an ActivityEvent object.

    Attributes:
    - model (class): The model representing the ActivityEvent object.
    - template_name (str): The template name to render for the delete confirmation page.

    Methods:
    - get_success_url: Returns the URL to redirect to after successfully deleting an ActivityEvent object.
    """
    model = ActivityEvent
    template_name = 'activityevent_confirm_delete.html'

    def get_success_url(self):
        activity_date = self.object.activity_date
        return reverse('day', kwargs={'date': activity_date.strftime("%Y-%m-%d")})


def add_emotion_view(request, activity_id):
    """
    Renders the add emotion view for a specific activity.

    Args:
        request (HttpRequest): The HTTP request object.
        activity_id (int): The ID of the activity.

    Returns:
        HttpResponse: The HTTP response object.

    Raises:
        Http404: If the activity event with the given ID does not exist.
    """
    activity_event = get_object_or_404(ActivityEvent, id=activity_id)
    activity = activity_event.activity
    current_date = activity_event.activity_date
    if request.method == 'POST':
        form = UserActivityEmotionForm(request.POST)
        if form.is_valid():
            emotion = form.save(activityevent=activity_event, commit=False)
            emotion.user = request.user
            emotion.activity = activity
            emotion.save()
            return redirect('day', date=current_date.strftime("%Y-%m-%d"))
    else:
        form = UserActivityEmotionForm()
    ctx = {'activity': activity, 'form': form}
    return render(request, 'add_emotion_to_activity.html', ctx)


class WeekView(TemplateView):
    """
    A class representing a view for displaying a weekly calendar.

    Attributes:
        template_name (str): The name of the template to use for rendering the week view.

    Methods:
        get_context_data(**kwargs):
            Retrieves the context data for rendering the week view.

            Args:
                **kwargs: Additional keyword arguments.

            Returns:
                dict: A dictionary containing the context data for rendering the week view.
    """
    template_name = 'week_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        start_week = self.kwargs.get('date', timezone.now().date())
        if isinstance(start_week, str):
            try:
                start_week = datetime.strptime(start_week, '%Y-%m-%d').date()
            except ValueError:
                print('Incorrect date format, should be YYYY-MM-DD')
                start_week = timezone.now().date()

        end_week = start_week + timedelta(days=6)

        context['start_week'] = start_week
        context['end_week'] = end_week

        is_current_week = start_week <= timezone.now().date() <= end_week
        context['is_current_week'] = is_current_week

        # Calculate the start date of the previous week and next week based on the specified date
        prev_week_start = start_week - timedelta(days=7)
        next_week_start = start_week + timedelta(days=7)

        # compute all dates in current week and filter activities that fall in current week
        week_dates = [start_week + timedelta(days=i) for i in range(7)]
        week_activities = ActivityEvent.objects.filter(activity_date__range=(start_week, end_week),
                                                       user=self.request.user)

        # create a dictionary where keys are dates and values are list of activities
        activities_by_date = defaultdict(list)
        for activity in week_activities:
            activities_by_date[activity.activity_date].append(activity)

        # convert activities_by_date dictionary into a list of tuples for the template
        context['week_dates_with_activities'] = [(date, activities_by_date[date]) for date in week_dates]

        # add the start date of the previous week and next week to the context
        context['prev_week'] = prev_week_start.strftime("%Y-%m-%d")
        context['next_week'] = next_week_start.strftime("%Y-%m-%d")

        return context

