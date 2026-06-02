from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("accounts/", include("accounts.urls")),
    path("assets/", include("assets.urls")),
    path("liabilities/", include("liabilities.urls")),
    path("equity/", include("equity.urls")),
    path("calculators/", include("calculators.urls")),
    path("budget/", include("budget.urls")),
    path("projects/", include("projects.urls")),

    # Main dashboard and landing pages
    path("", include("dashboard.urls")),
]
