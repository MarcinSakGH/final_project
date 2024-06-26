from django.urls import path
from .views import (SignUpView, CustomUserUpdateView, ActivityListView, ActivityCreateView, ActivityUpdateView,
                    ActivityDeleteView, add_activity, ActivityEventDeleteView, DayView, CustomLoginView,
                    add_emotion_view, WeekView, ActivityEventUpdateView, chatbot_view, SummaryDetailView,
                    day_summary_pdf_view, SummaryRangeView, RangeSummaryPDFView)
from django.contrib.auth.views import LogoutView, LoginView


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
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
    path('summary/<int:summary_id>/', day_summary_pdf_view, name='day-summary-pdf'),
    path('summaries/', SummaryRangeView.as_view(), name='range-summary-view'),
    path('summaries/pdf/<str:start_date>/<str:end_date>/', RangeSummaryPDFView.as_view(), name='range-summary-pdf'),
]