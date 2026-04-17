from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('net-worth/', views.net_worth_summary, name='net_worth'),
]
