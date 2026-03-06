"""src/core/urls.py."""

from django.urls import path

from .views import AuthActionView
from .views import IndexView
from .views import UserLogoutView

app_name = "core"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("auth/", AuthActionView.as_view(), name="auth_action"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]
