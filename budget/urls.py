from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.budget_dashboard,
        name='budget_menu'
    ),

    path(
        'accounts/',
        views.manage_accounts,
        name='manage_accounts'
    ),

    path(
        'accounts/edit/<int:pk>/',
        views.edit_account,
        name='edit_account'
    ),

    path(
        'accounts/delete/<int:pk>/',
        views.delete_account,
        name='delete_account'
    ),

    path(
        'diary/',
        views.transactions_diary,
        name='transactions_diary'
    ),

    path(
        'diary/edit/<int:pk>/',
        views.edit_transaction,
        name='edit_transaction'
    ),

    path(
        'diary/delete/<int:pk>/',
        views.delete_transaction,
        name='delete_transaction'
    ),

]
