from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('assets/', include('assets.urls')),
    path('liabilities/', include('liabilities.urls')),
    path('equity/', include('equity.urls')),
    path('calculators/', include('calculators.urls')),

    path('budget/', include('budget.urls')),

    # path('glossary/', include('glossary.urls')),
    path('projects/', include('projects.urls')),

    path('', include('dashboard.urls')),
]
