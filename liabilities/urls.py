from django.urls import path
from . import views

urlpatterns = [
    path('', views.manage_liabilities, name='manage_liabilities'),
    path('edit/<int:pk>/', views.edit_liability, name='edit_liability'),
    path('delete/<int:pk>/', views.delete_liability, name='delete_liability'),
]
