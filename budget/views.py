from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction, Account
from .forms import TransactionForm, AccountForm

# --- 1. THE FACE: BUDGET MENU (DASHBOARD) ---


@login_required
def budget_dashboard(request):
    user_accounts = Account.objects.filter(user=request.user)

    # FIXED: Replaced 'balance' with 'initial_balance'
    liquid_total = user_accounts.filter(account_class='LIQUID').aggregate(
        Sum('initial_balance'))['initial_balance__sum'] or 0
    debt_total = user_accounts.filter(account_class='DEBT').aggregate(
        Sum('initial_balance'))['initial_balance__sum'] or 0

    context = {
        'liquid_total': liquid_total,
        'debt_total': debt_total,
        'net_worth': liquid_total - debt_total,
        'accounts': user_accounts,
    }
    return render(request, 'budget/budget_menu.html', context)


# --- 2. MANAGE LIQUIDITY & DEBT (The Setup) ---

@login_required
def manage_accounts(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            new_account = form.save(commit=False)
            new_account.user = request.user
            new_account.save()
            messages.success(
                request, f"Account '{new_account.name}' registered successfully!")
            return redirect('manage_accounts')
    else:
        form = AccountForm()

    accounts = Account.objects.filter(user=request.user)
    return render(request, 'budget/manage_accounts.html', {'form': form, 'accounts': accounts})


# --- THE NEW EDIT ACCOUNT FUNCTION ---

@login_required
def edit_account(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)

    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Account '{account.name}' updated successfully!")
            return redirect('manage_accounts')
    else:
        form = AccountForm(instance=account)

    return render(request, 'budget/edit_account.html', {'form': form, 'account': account})


# --- 3. TRANSACTION DIARY (The Flow) ---

@login_required
def transactions_diary(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user

            # --- UPDATE THE ACCOUNT BALANCE ---
            if transaction.account:
                # FIXED: Replaced 'balance' with 'initial_balance'
                if transaction.transaction_type == 'REVENUE':
                    transaction.account.initial_balance += transaction.amount
                elif transaction.transaction_type == 'EXPENSE':
                    transaction.account.initial_balance -= transaction.amount

                transaction.account.save()

            transaction.save()
            messages.success(
                request, 'Transaction logged and balance updated!')
            return redirect('transactions_diary')
    else:
        form = TransactionForm(user=request.user)

    transactions = Transaction.objects.filter(
        user=request.user).order_by('-date')
    return render(request, 'budget/transactions_diary.html', {'form': form, 'transactions': transactions})


# --- UTILITIES ---

@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    original_amount = transaction.amount
    original_type = transaction.transaction_type
    original_account = transaction.account

    if request.method == 'POST':
        form = TransactionForm(
            request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            # 1. Reverse the old impact on the account
            if original_account:
                # FIXED: Replaced 'balance' with 'initial_balance'
                if original_type == 'REVENUE':
                    original_account.initial_balance -= original_amount
                else:
                    original_account.initial_balance += original_amount
                original_account.save()

            # 2. Save new transaction data
            updated_transaction = form.save()

            # 3. Apply the new impact to the account
            if updated_transaction.account:
                # FIXED: Replaced 'balance' with 'initial_balance'
                if updated_transaction.transaction_type == 'REVENUE':
                    updated_transaction.account.initial_balance += updated_transaction.amount
                else:
                    updated_transaction.account.initial_balance -= updated_transaction.amount
                updated_transaction.account.save()

            messages.success(request, 'Transaction and balance updated!')
            return redirect('transactions_diary')
    else:
        form = TransactionForm(instance=transaction, user=request.user)

    return render(request, 'budget/edit_transaction.html', {'form': form, 'transaction': transaction})


@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        # --- REVERSE THE BALANCE BEFORE DELETING ---
        if transaction.account:
            # FIXED: Replaced 'balance' with 'initial_balance'
            if transaction.transaction_type == 'REVENUE':
                transaction.account.initial_balance -= transaction.amount
            else:
                transaction.account.initial_balance += transaction.amount
            transaction.account.save()

        transaction.delete()
        messages.success(request, 'Transaction deleted and balance restored.')
    return redirect('transactions_diary')
