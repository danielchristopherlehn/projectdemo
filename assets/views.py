from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Asset
from .forms import AssetForm
from budget.models import Account

# Nicer names for the current asset types (used to group them on the page).
TYPE_LABELS = {
    'CASH': 'Physical Cash',
    'CHECKING': 'Checking Accounts',
    'SAVINGS': 'Savings Accounts',
    'E-WALLET': 'Digital Wallets',
}


@login_required
def manage_assets(request):
    # All the long term assets that belong to this user.
    long_term_assets = Asset.objects.filter(user=request.user)
    long_term_total = long_term_assets.aggregate(
        total=Sum('value_estimate'))['total'] or 0

    # Add up the value per asset type so I can draw the allocation bar.
    type_data = list(
        long_term_assets.values('asset_type').annotate(
            total=Sum('value_estimate')
        ).order_by('-total')
    )

    # Build the coloured bar showing what percent each type is.
    colors = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4']
    allocation_bar = []
    index = 0
    for item in type_data:
        item_total = item['total'] or 0
        # Work out the percentage of the total (avoid dividing by zero).
        if long_term_total > 0:
            percentage = float(item_total) / float(long_term_total) * 100
        else:
            percentage = 0
        allocation_bar.append({
            'name': item['asset_type'],
            'total': item_total,
            'percentage': round(percentage, 2),
            # Pick a colour, wrap back to the start if we run out.
            'color': colors[index % len(colors)],
        })
        index += 1

    # The current asset accounts come from the budget app.
    current_assets = Account.objects.filter(
        user=request.user, account_class='CURRENT_ASSET')

    # Sorting for the current assets list.
    ca_sort = request.GET.get('ca_sort', 'balance_desc')
    ca_sort_map = {
        'balance_desc': '-initial_balance',
        'balance_asc':  'initial_balance',
        'name_asc':     'name',
    }
    current_assets = current_assets.order_by(
        ca_sort_map.get(ca_sort, '-initial_balance'))

    # Group the current assets by their type label.
    current_asset_groups = {}
    for account in current_assets:
        label = TYPE_LABELS.get(account.account_type, account.account_type)
        if label not in current_asset_groups:
            current_asset_groups[label] = []
        current_asset_groups[label].append(account)

    current_assets_total = current_assets.aggregate(
        total=Sum('initial_balance'))['total'] or 0

    # Sorting for the long term assets list.
    sort = request.GET.get('sort', 'value_desc')
    sort_map = {
        'value_desc': '-value_estimate',
        'value_asc':  'value_estimate',
        'year_desc':  '-purchase_year',
        'year_asc':   'purchase_year',
        'name_asc':   'asset_name',
    }
    long_term_assets = long_term_assets.order_by(
        sort_map.get(sort, '-value_estimate'))

    context = {
        'long_term_assets': long_term_assets,
        'long_term_total': long_term_total,
        'allocation_bar': allocation_bar,
        'current_asset_groups': current_asset_groups,
        'current_assets_total': current_assets_total,
        'current_sort': sort,
        'ca_sort': ca_sort,
    }
    return render(request, 'assets/manage_assets.html', context)


@login_required
def add_asset(request):
    if request.method == 'POST':
        form = AssetForm(request.POST, user=request.user)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.user = request.user
            asset.save()
            messages.success(request, f"'{asset.asset_name}' registered.")
            return redirect('manage_assets')
    else:
        form = AssetForm(user=request.user)
    return render(request, 'assets/add_asset.html', {'form': form})


@login_required
def edit_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{asset.asset_name}' updated.")
            return redirect('manage_assets')
    else:
        form = AssetForm(instance=asset, user=request.user)
    return render(request, 'assets/add_asset.html', {'form': form, 'asset': asset, 'editing': True})


@login_required
def delete_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk, user=request.user)
    if request.method == 'POST':
        asset.delete()
        messages.success(request, "Asset deleted.")
    return redirect('manage_assets')
