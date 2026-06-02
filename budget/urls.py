from django.urls import path
from . import views

urlpatterns = [
    path('', views.budget_dashboard, name='budget_menu'),
    path('accounts/add/', views.manage_accounts, name='manage_accounts'),
    path('accounts/edit/<int:pk>/', views.edit_account, name='edit_account'),
    path('accounts/delete/<int:pk>/', views.delete_account, name='delete_account'),
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('transactions/edit/<int:pk>/',
         views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:pk>/',
         views.delete_transaction, name='delete_transaction'),
    path('transfers/', views.transfers_list, name='transfers_list'),
    path('pay-card/', views.pay_card, name='pay_card'),
]
