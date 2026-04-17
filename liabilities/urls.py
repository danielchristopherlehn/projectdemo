from django.urls import path
from . import views

urlpatterns = [
    # The main page that lists all liabilities and has the add form
    path('', views.manage_liabilities, name='manage_liabilities'),

    # The URL to edit a specific liability (the <int:pk> catches the ID number)
    path('edit/<int:pk>/', views.edit_liability, name='edit_liability'),

    # The URL to delete a specific liability
    path('delete/<int:pk>/', views.delete_liability, name='delete_liability'),
]
