from django.urls import path
from . import views


urlpatterns = [

    # MAIN BUDGET DASHBOARD
    path(
        '',
        views.budget_dashboard,
        name='budget_menu'
    ),

    # ACCOUNT MANAGEMENT
    path(
        'accounts/',
        views.manage_accounts,
        name='manage_accounts'
    ),

    # EDIT ACCOUNT
    path(
        'accounts/edit/<int:pk>/',
        views.edit_account,
        name='edit_account'
    ),

    # DELETE ACCOUNT
    path(
        'accounts/delete/<int:pk>/',
        views.delete_account,
        name='delete_account'
    ),

    # TRANSACTION DIARY
    path(
        'diary/',
        views.transactions_diary,
        name='transactions_diary'
    ),

    # EDIT TRANSACTION
    path(
        'diary/edit/<int:pk>/',
        views.edit_transaction,
        name='edit_transaction'
    ),

    # DELETE TRANSACTION
    path(
        'diary/delete/<int:pk>/',
        views.delete_transaction,
        name='delete_transaction'
    ),

]
