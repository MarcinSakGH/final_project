from django.urls import path
from .views import (SignUpView, CustomUserUpdateView, ActivityListView, ActivityCreateView, ActivityUpdateView,
                    ActivityDeleteView)
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/update/', CustomUserUpdateView.as_view(), name='user-update'),
    path('activities/', ActivityListView.as_view(), name='activity_list'),
    path('activities/new/', ActivityCreateView.as_view(), name='activity_create'),
    path('activities/edit/<int:pk>', ActivityUpdateView.as_view(), name='activity_update'),
    path('activities/delete/<int:pk>', ActivityDeleteView.as_view(), name='activity_delete'),
]