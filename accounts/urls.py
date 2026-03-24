from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import path

from .views import register_view


def redirect_to_admin_login(request):
    return redirect("/admin/login/")

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", redirect_to_admin_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
