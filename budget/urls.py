from django.urls import path
from . import views

urlpatterns = [
    # 1. THE FACE: The main entry point for the budget app
    path('', views.budget_dashboard, name='budget_menu'),

    # 2. THE SETUP: Where user manages bank accounts, cash, and credit cards
    path('accounts/', views.manage_accounts, name='manage_accounts'),

    # FIXED: Added the specific route for editing an account
    path('accounts/edit/<int:pk>/', views.edit_account, name='edit_account'),

    # 3. THE FLOW: The transaction diary
    path('diary/', views.transactions_diary, name='transactions_diary'),

    # Utilities for the diary
    path('diary/edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('diary/delete/<int:pk>/', views.delete_transaction,
         name='delete_transaction'),
]
