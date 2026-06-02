from django.urls import path
from . import views

urlpatterns = [
    path('', views.manage_assets, name='manage_assets'),
    path('add/', views.add_asset, name='add_asset'),
    path('edit/<int:pk>/', views.edit_asset, name='edit_asset'),
    path('delete/<int:pk>/', views.delete_asset, name='delete_asset'),
]
