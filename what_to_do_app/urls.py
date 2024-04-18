from django.urls import path
from .views import (SignUpView, CustomUserUpdateView, ActivityListView, ActivityCreateView, ActivityUpdateView,
                    ActivityDeleteView, add_activity, ActivityEventDeleteView, DayView, CustomLoginView,
                    add_emotion_view, WeekView, ActivityEventUpdateView, chatbot_view, SummaryDetailView)
from django.contrib.auth.views import LogoutView, LoginView


urlpatterns = [
    path('login', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/update/', CustomUserUpdateView.as_view(), name='user-update'),
    path('activities/', ActivityListView.as_view(), name='activity_list'),
    path('activities/new/', ActivityCreateView.as_view(), name='activity_create'),
    path('activities/edit/<int:pk>', ActivityUpdateView.as_view(), name='activity_update'),
    path('activities/delete/<int:pk>', ActivityDeleteView.as_view(), name='activity_delete'),
    path('current_day/', DayView.as_view(), name='current_day'),
    path('day/<str:date>/', DayView.as_view(), name='day'),
    path('add_activity/', add_activity, name='add_activity'),
    path('activity_event/delete/<int:pk>', ActivityEventDeleteView.as_view(), name='activity_event_delete'),
    path('add_emotion/<int:activity_id>/', add_emotion_view, name='add_emotion'),
    path('week/', WeekView.as_view(), name='week'),
    path('week/<str:date>/', WeekView.as_view(), name='week_view'),
    path('activity_event/edit/<int:pk>/', ActivityEventUpdateView.as_view(), name='activity_event_update'),
    path('chatbot/', chatbot_view, name='chatbot'),
    path('summary-detail', SummaryDetailView.as_view(), name='summary-detail'),
]