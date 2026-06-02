from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date as today_date

from .models import Transaction, Account
from .forms import TransactionForm, AccountForm, TransferForm, PayCardForm

# Labels and order I use to group the accounts on the budget dashboard.
ASSET_TYPE_LABELS = {
    'CASH': 'Physical Cash',
    'CHECKING': 'Checking Accounts',
    'SAVINGS': 'Savings Accounts',
    'E-WALLET': 'Digital Wallets',
}
LIABILITY_TYPE_LABELS = {
    'CREDIT_CARD': 'Credit Cards',
    'OVERDRAFT': 'Bank Overdrafts',
    'LINE_OF_CREDIT': 'Lines of Credit',
}
ASSET_TYPE_ORDER = ['CASH', 'CHECKING', 'SAVINGS', 'E-WALLET']
LIABILITY_TYPE_ORDER = ['CREDIT_CARD', 'OVERDRAFT', 'LINE_OF_CREDIT']


# When a transaction happens, the money on the account has to move.
# Revenue adds money to the account. Expense takes money out of an asset
# account, but for a liability (credit card) it makes the debt bigger.
# A Transfer takes money from one account and puts it in another.
def apply_to_balance(transaction):
    account = transaction.account
    dest = transaction.destination_account
    amount = transaction.amount

    if transaction.transaction_type == 'REVENUE':
        account.initial_balance += amount
        account.save()

    elif transaction.transaction_type == 'EXPENSE':
        if account.account_class == 'CURRENT_ASSET':
            account.initial_balance -= amount
        else:
            # Spending on a credit card increases what you owe.
            account.initial_balance += amount
        account.save()

    elif transaction.transaction_type == 'TRANSFER' and dest:
        # Money leaves the source account.
        account.initial_balance -= amount
        account.save()
        # And arrives in the destination. If the destination is a credit card,
        # the money pays off the debt instead of adding to a balance.
        if dest.account_class == 'CURRENT_ASSET':
            dest.initial_balance += amount
        else:
            dest.initial_balance -= amount
        dest.save()


# This does the opposite of apply_to_balance. I use it when a transaction is
# deleted or edited so the old balances get put back the way they were.
def undo_from_balance(transaction):
    account = transaction.account
    dest = transaction.destination_account
    amount = transaction.amount

    if transaction.transaction_type == 'REVENUE':
        account.initial_balance -= amount
        account.save()

    elif transaction.transaction_type == 'EXPENSE':
        if account.account_class == 'CURRENT_ASSET':
            account.initial_balance += amount
        else:
            account.initial_balance -= amount
        account.save()

    elif transaction.transaction_type == 'TRANSFER' and dest:
        account.initial_balance += amount
        account.save()
        if dest.account_class == 'CURRENT_ASSET':
            dest.initial_balance -= amount
        else:
            dest.initial_balance += amount
        dest.save()


# Before saving an expense I check the account can handle it. For an asset
# account you can't go below 0, and for a credit card you can't go over the
# credit limit. Returns an error message, or None if everything is fine.
def check_funds(t_type, account, amount):
    if t_type == 'EXPENSE':
        if account.account_class == 'CURRENT_ASSET':
            if account.initial_balance - amount < 0:
                return (f"Insufficient funds in '{account.name}'. "
                        f"Available: ${account.initial_balance:.2f}")
        else:
            if account.credit_limit is not None:
                if account.initial_balance + amount > account.credit_limit:
                    remaining = account.credit_limit - account.initial_balance
                    return (f"Exceeds credit limit on '{account.name}'. "
                            f"Available credit: ${remaining:.2f}")
    return None


@login_required
def budget_dashboard(request):
    # Split the user's accounts into assets and liabilities.
    current_assets = Account.objects.filter(
        user=request.user, account_class='CURRENT_ASSET')
    current_liabilities = Account.objects.filter(
        user=request.user, account_class='CURRENT_LIABILITY')

    # Totals for the banner at the top.
    assets_total = current_assets.aggregate(t=Sum('initial_balance'))['t'] or 0
    liabilities_total = current_liabilities.aggregate(
        t=Sum('initial_balance'))['t'] or 0
    working_capital = assets_total - liabilities_total

    # Group the asset accounts by their type (cash, checking, etc).
    asset_groups = []
    for type_key in ASSET_TYPE_ORDER:
        accounts = current_assets.filter(account_type=type_key)
        if accounts.exists():
            asset_groups.append({
                'label': ASSET_TYPE_LABELS[type_key],
                'accounts': accounts,
                'total': accounts.aggregate(t=Sum('initial_balance'))['t'] or 0,
            })

    # Same thing but for the liability accounts.
    liability_groups = []
    for type_key in LIABILITY_TYPE_ORDER:
        accounts = current_liabilities.filter(account_type=type_key)
        if accounts.exists():
            liability_groups.append({
                'label': LIABILITY_TYPE_LABELS[type_key],
                'accounts': accounts,
                'total': accounts.aggregate(t=Sum('initial_balance'))['t'] or 0,
            })

    context = {
        'assets_total': assets_total,
        'liabilities_total': liabilities_total,
        'working_capital': working_capital,
        'asset_groups': asset_groups,
        'liability_groups': liability_groups,
    }
    return render(request, 'budget/budget_menu.html', context)


@login_required
def manage_accounts(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            messages.success(request, f"Account '{account.name}' created.")
            return redirect('budget_menu')
    else:
        form = AccountForm()
    return render(request, 'budget/manage_accounts.html', {'form': form})


@login_required
def edit_account(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, f"Account '{account.name}' updated.")
            return redirect('budget_menu')
    else:
        form = AccountForm(instance=account)
    return render(request, 'budget/edit_account.html', {'form': form, 'account': account})


@login_required
def delete_account(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)
    if request.method == 'POST':
        account.delete()
        messages.success(request, "Account deleted.")
    return redirect('budget_menu')


@login_required
def transactions_list(request):
    # Handle a new transaction being added from the form.
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            # Check there is enough money / credit before saving.
            error = check_funds(
                transaction.transaction_type,
                transaction.account,
                transaction.amount,
            )
            if error:
                messages.error(request, error)
            else:
                transaction.save()
                apply_to_balance(transaction)
                messages.success(request, 'Transaction saved.')
                return redirect('transactions_list')
    else:
        form = TransactionForm(user=request.user)

    # Get all the transactions for this user, but not transfers (those have
    # their own page).
    transactions = Transaction.objects.filter(
        user=request.user
    ).exclude(transaction_type='TRANSFER')

    # --- FILTERS ---
    account_filter = request.GET.get('account', '')
    type_filter = request.GET.get('type', '')
    country_filter = request.GET.get('country', '')
    sort = request.GET.get('sort', 'date_desc')

    if account_filter:
        transactions = transactions.filter(account__pk=account_filter)
    if type_filter:
        transactions = transactions.filter(transaction_type=type_filter)
    if country_filter:
        transactions = transactions.filter(account__country=country_filter)

    # Sort the list depending on what the user picked in the dropdown.
    if sort == 'date_asc':
        transactions = transactions.order_by('date', 'id')
    elif sort == 'amount_desc':
        transactions = transactions.order_by('-amount')
    elif sort == 'amount_asc':
        transactions = transactions.order_by('amount')
    else:
        # Default: newest first.
        transactions = transactions.order_by('-date', '-id')

    user_accounts = Account.objects.filter(
        user=request.user,
        account_class__in=['CURRENT_ASSET', 'CURRENT_LIABILITY']
    )
    countries = user_accounts.values_list(
        'country', 'country').distinct().order_by('country')

    return render(request, 'budget/transactions_list.html', {
        'form': form,
        'transactions': transactions,
        'user_accounts': user_accounts,
        'countries': countries,
        'current_sort': sort,
        'current_account': account_filter,
        'current_type': type_filter,
        'current_country': country_filter,
    })


@login_required
def transfers_list(request):
    # A transfer moves money from one of your accounts to another.
    if request.method == 'POST':
        form = TransferForm(request.POST, user=request.user)
        if form.is_valid():
            source = form.cleaned_data['source_account']
            dest = form.cleaned_data['destination_account']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '')
            txn_date = form.cleaned_data['date']

            transaction = Transaction(
                user=request.user,
                account=source,
                destination_account=dest,
                date=txn_date,
                transaction_type='TRANSFER',
                category='',
                description=description,
                amount=amount,
            )
            transaction.save()
            apply_to_balance(transaction)
            messages.success(
                request,
                f"Transfer of ${amount:.2f} from '{source.name}' to '{dest.name}' completed."
            )
            return redirect('transfers_list')
    else:
        form = TransferForm(user=request.user)

    transfers = Transaction.objects.filter(
        user=request.user,
        transaction_type='TRANSFER'
    ).order_by('-date', '-id')

    # The credit cards / liabilities the user can pay off.
    cards = Account.objects.filter(
        user=request.user, account_class='CURRENT_LIABILITY')

    return render(request, 'budget/transfers.html', {
        'form': form,
        'pay_card_form': PayCardForm(
            user=request.user, initial={'date': today_date.today()}),
        'transfers': transfers,
        'cards': cards,
    })


@login_required
def pay_card(request):
    # This handles the "Pay a Card" form on the transfers page.
    if request.method != 'POST':
        return redirect('transfers_list')

    form = PayCardForm(request.POST, user=request.user)
    if not form.is_valid():
        # Something was wrong with the form, show the first error.
        for field in form.errors:
            messages.error(request, form.errors[field][0])
        return redirect('transfers_list')

    source = form.cleaned_data['source_account']
    card = form.cleaned_data['card']
    pay_full = form.cleaned_data['pay_full']
    entered = form.cleaned_data.get('amount')
    apply_penalty = form.cleaned_data['apply_penalty']
    txn_date = form.cleaned_data['date']

    # The card balance is how much money is still owed on it.
    owed = card.initial_balance
    if owed <= 0:
        messages.error(request, f"'{card.name}' has nothing to pay.")
        return redirect('transfers_list')

    # Work out how much we actually pay.
    if pay_full:
        payment = owed
    else:
        payment = entered
        # You can't pay more than what you owe. If the user types too much,
        # just pay the full debt and ignore the rest.
        if payment > owed:
            payment = owed

    # Some cards have a penalty fee from the bank. Only add it if the card
    # has one and the user left the box ticked.
    penalty = 0
    if apply_penalty and card.payment_penalty > 0:
        penalty = card.payment_penalty
    total_debit = payment + penalty

    # Make sure the paying account has enough money for the payment + penalty.
    if source.initial_balance < total_debit:
        messages.error(
            request,
            f"Not enough money in '{source.name}'. "
            f"You need ${total_debit:.2f} but only have ${source.initial_balance:.2f}."
        )
        return redirect('transfers_list')

    # Save the payment as a transfer from the account to the card.
    payment_txn = Transaction(
        user=request.user,
        account=source,
        destination_account=card,
        date=txn_date,
        transaction_type='TRANSFER',
        category='',
        description=f"Card payment - {card.name}",
        amount=payment,
    )
    payment_txn.save()
    apply_to_balance(payment_txn)

    # If there is a penalty, save it as a normal expense on the paying account.
    if penalty:
        penalty_txn = Transaction(
            user=request.user,
            account=source,
            date=txn_date,
            transaction_type='EXPENSE',
            category='OTHER',
            description=f"Penalty fee - {card.name}",
            amount=penalty,
        )
        penalty_txn.save()
        apply_to_balance(penalty_txn)

    # Build a message telling the user what happened.
    card.refresh_from_db()
    message = f"Paid ${payment:.2f} to '{card.name}'."
    if penalty:
        message += f" Penalty fee ${penalty:.2f} charged."
    message += f" Remaining card balance: ${card.initial_balance:.2f}."
    messages.success(request, message)
    return redirect('transfers_list')


@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(
            request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            updated = form.save(commit=False)
            error = check_funds(
                updated.transaction_type,
                updated.account,
                updated.amount,
            )
            if error:
                messages.error(request, error)
            else:
                # Undo the old version first, then apply the new one so the
                # balances stay correct.
                undo_from_balance(transaction)
                updated.save()
                apply_to_balance(updated)
                messages.success(request, 'Transaction updated.')
                return redirect('transactions_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)

    return render(request, 'budget/edit_transaction.html', {
        'form': form,
        'transaction': transaction,
    })


@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        # Put the money back before deleting the record.
        undo_from_balance(transaction)
        transaction.delete()
        messages.success(request, 'Transaction deleted and balances restored.')
    return redirect('transactions_list')
