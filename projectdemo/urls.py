"""
URL configuration for projectdemo project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("assets/", include("assets.urls")),
    path("liabilities/", include("liabilities.urls")),  # <-- ADDED THIS LINE
    path("glossary/", include("main.urls")),
    path("", include("dashboard.urls")),
    path("projects/", include("projects.urls")),
]
