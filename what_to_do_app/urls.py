from django.urls import path
from .views import SignUpView, CustomUserUpdateView
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/update/', CustomUserUpdateView.as_view(), name='user-update')
]