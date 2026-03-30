from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from .models import Asset
from .forms import AssetForm


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

    user_assets = Asset.objects.filter(user=request.user)

    # Calculate Total Portfolio Value
    total_value = user_assets.aggregate(Sum('purchase_price'))[
        'purchase_price__sum'] or 0

    # Group by type for the distribution bar AND the chart
    type_counts = user_assets.values('asset_type').annotate(
        total=Count('id')).order_by('asset_type')

    # NEW: Prepare specific lists for the JavaScript Pie Chart
    chart_labels = [item['asset_type'] for item in type_counts]
    chart_data = [item['total'] for item in type_counts]

    context = {
        'form': form,
        'assets': user_assets,
        'total_value': total_value,
        'type_counts': type_counts,
        'chart_labels': chart_labels,  # Sent as a Python list
        'chart_data': chart_data,      # Sent as a Python list
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
    return render(request, 'assets/edit_asset.html', {'form': form, 'asset': asset})


@login_required
def delete_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk, user=request.user)
    asset.delete()
    return redirect('manage_assets')
