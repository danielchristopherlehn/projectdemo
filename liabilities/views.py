from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Liability
from .forms import LiabilityForm
from budget.models import Account

LIABILITY_TYPE_ORDER = ['CREDIT_CARD', 'OVERDRAFT', 'LINE_OF_CREDIT']
LIABILITY_TYPE_LABELS = {
    'CREDIT_CARD': 'Credit Cards',
    'OVERDRAFT': 'Bank Overdrafts',
    'LINE_OF_CREDIT': 'Lines of Credit',
}

LONG_TERM_COLORS = {
    'Mortgage': '#002D62',
    'Car Loan': '#3b82f6',
    'Student Loan': '#8b5cf6',
    'Credit Card': '#ef4444',
    'Other': '#6b7280',
}


@login_required
def manage_liabilities(request):
    if request.method == 'POST':
        form = LiabilityForm(request.POST, user=request.user)
        if form.is_valid():
            liability = form.save(commit=False)
            liability.user = request.user
            liability.save()
            return redirect('manage_liabilities')
    else:
        form = LiabilityForm(user=request.user)

    # Long-term liabilities
    long_term = Liability.objects.filter(user=request.user)
    long_term_total = long_term.aggregate(
        total=Sum('principal_amount'))['total'] or 0

    # Allocation bar
    type_data = {}
    for item in long_term:
        type_data[item.liability_type] = type_data.get(
            item.liability_type, 0) + float(item.principal_amount)

    allocation_bar = []
    for ltype, total in sorted(type_data.items(), key=lambda x: -x[1]):
        percentage = (total / float(long_term_total) *
                      100) if long_term_total > 0 else 0
        allocation_bar.append({
            'name': ltype,
            'total': total,
            'percentage': round(percentage, 2),
            'color': LONG_TERM_COLORS.get(ltype, '#6b7280'),
        })

    # Current liabilities from Budget (read-only, redirect to My Budget)
    current_liabilities = Account.objects.filter(
        user=request.user, account_class='CURRENT_LIABILITY')

    current_groups = []
    for type_key in LIABILITY_TYPE_ORDER:
        accounts = current_liabilities.filter(account_type=type_key)
        if accounts.exists():
            current_groups.append({
                'label': LIABILITY_TYPE_LABELS[type_key],
                'accounts': accounts,
                'total': accounts.aggregate(t=Sum('initial_balance'))['t'] or 0,
            })

    current_liabilities_total = current_liabilities.aggregate(
        total=Sum('initial_balance'))['total'] or 0

    context = {
        'form': form,
        'long_term': long_term,
        'long_term_total': long_term_total,
        'allocation_bar': allocation_bar,
        'current_groups': current_groups,
        'current_liabilities_total': current_liabilities_total,
    }
    return render(request, 'liabilities/manage_liabilities.html', context)


@login_required
def add_liability(request):
    if request.method == 'POST':
        form = LiabilityForm(request.POST, user=request.user)
        if form.is_valid():
            liability = form.save(commit=False)
            liability.user = request.user
            liability.save()
            messages.success(request, f"'{liability.liability_name}' registered.")
            return redirect('manage_liabilities')
    else:
        form = LiabilityForm(user=request.user)
    return render(request, 'liabilities/add_liability.html', {'form': form})


@login_required
def edit_liability(request, pk):
    liability = get_object_or_404(Liability, pk=pk, user=request.user)
    if request.method == 'POST':
        form = LiabilityForm(
            request.POST, instance=liability, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('manage_liabilities')
    else:
        form = LiabilityForm(instance=liability, user=request.user)
    return render(request, 'liabilities/edit_liability.html', {
        'form': form, 'liability': liability})


@login_required
def delete_liability(request, pk):
    liability = get_object_or_404(Liability, pk=pk, user=request.user)
    if request.method == 'POST':
        liability.delete()
    return redirect('manage_liabilities')
