from django.urls import path
from .views import (SignUpView, CustomUserUpdateView, ActivityListView, ActivityCreateView, ActivityUpdateView,
                    ActivityDeleteView, add_activity, ActivityEventDeleteView, DayView, CustomLoginView,
                    add_emotion_view)
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
]