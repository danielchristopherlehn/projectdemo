from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Asset
from .forms import AssetForm
from budget.models import Account


@login_required
def manage_assets(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            new_asset = form.save(commit=False)
            new_asset.user = request.user
            new_asset.save()
            return redirect('manage_assets')
    else:
        form = AssetForm()

    user_assets = Asset.objects.filter(
        user=request.user
    ).exclude(asset_type='Bank Account')

    budget_accounts = Account.objects.filter(
        user=request.user,
        account_class='LIQUID'
    )

    assets_total = user_assets.aggregate(
        Sum('value_estimate')
    )['value_estimate__sum'] or 0

    accounts_total = budget_accounts.aggregate(
        Sum('initial_balance')
    )['initial_balance__sum'] or 0

    total_value = assets_total + accounts_total

    type_data = list(
        user_assets.values('asset_type').annotate(
            total=Sum('value_estimate')
        ).order_by('-total')
    )

    if accounts_total > 0:
        type_data.append({
            'asset_type': 'Bank Accounts (Budget)',
            'total': accounts_total
        })
        type_data.sort(key=lambda x: x['total'], reverse=True)

    allocation_bar = []
    colors = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4']

    for index, item in enumerate(type_data):
        item_total = item['total'] or 0
        if total_value > 0:
            percentage = (float(item_total) / float(total_value)) * 100
        else:
            percentage = 0

        allocation_bar.append({
            'name': item['asset_type'],
            'total': item_total,
            'percentage': round(percentage, 2),
            'color': colors[index % len(colors)]
        })

    cash_reserves = budget_accounts.filter(account_type='CASH')
    bank_accounts = budget_accounts.exclude(account_type='CASH')
    other_assets = user_assets

    context = {
        'form': form,
        'assets': user_assets,
        'total_value': total_value,
        'allocation_bar': allocation_bar,
        'bank_accounts': bank_accounts,
        'cash_reserves': cash_reserves,
        'other_assets': other_assets,
    }

    return render(request, 'assets/manage_assets.html', context)


@login_required
def edit_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk, user=request.user)

    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            return redirect('manage_assets')
    else:
        form = AssetForm(instance=asset)

    return render(request, 'assets/edit_asset.html', {
        'form': form,
        'asset': asset
    })


@login_required
def delete_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk, user=request.user)
    asset.delete()
    return redirect('manage_assets')
