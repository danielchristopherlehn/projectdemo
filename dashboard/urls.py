from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('net-worth/', views.net_worth_summary, name='net_worth'),
    path('contact/', views.contact_us, name='contact_us'),
    path('glossary/', views.glossary, name='glossary'),]