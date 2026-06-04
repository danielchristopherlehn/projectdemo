from django.urls import path
from . import views

urlpatterns = [
    path('', views.manage_equity, name='manage_equity'),
    path('add/', views.add_equity, name='add_equity'),
    path('edit/<int:pk>/', views.edit_equity, name='edit_equity'),
    path('delete/<int:pk>/', views.delete_equity, name='delete_equity'),
]
