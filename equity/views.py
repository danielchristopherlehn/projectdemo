from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Equity
from .forms import EquityForm


@login_required
def manage_equity(request):
    # All equity records that belong to this user.
    equity_records = Equity.objects.filter(user=request.user)
    total_equity = equity_records.aggregate(total=Sum('amount'))['total'] or 0

    # Add up the amount per equity type so I can draw the allocation bar.
    type_data = list(
        equity_records.values('equity_type').annotate(
            total=Sum('amount')
        ).order_by('-total')
    )

    # Build the coloured bar showing what percent each type is (brown shades).
    colors = ['#442200', '#6b4423', '#8b5a2b', '#a9784e', '#c89b6e', '#e0bf99']
    allocation_bar = []
    index = 0
    for item in type_data:
        item_total = item['total'] or 0
        # Work out the percentage of the total (avoid dividing by zero).
        if total_equity > 0:
            percentage = float(item_total) / float(total_equity) * 100
        else:
            percentage = 0
        allocation_bar.append({
            'name': item['equity_type'],
            'total': item_total,
            'percentage': round(percentage, 2),
            # Pick a colour, wrap back to the start if we run out.
            'color': colors[index % len(colors)],
        })
        index += 1

    # Sorting for the equity list.
    sort = request.GET.get('sort', 'amount_desc')
    sort_map = {
        'amount_desc': '-amount',
        'amount_asc':  'amount',
        'name_asc':    'equity_name',
        'type_asc':    'equity_type',
    }
    equity_records = equity_records.order_by(sort_map.get(sort, '-amount'))

    context = {
        'equity_records': equity_records,
        'total_equity': total_equity,
        'allocation_bar': allocation_bar,
        'source_count': equity_records.count(),
        'current_sort': sort,
    }
    return render(request, 'equity/manage_equity.html', context)


@login_required
def add_equity(request):
    if request.method == 'POST':
        form = EquityForm(data=request.POST)
        if form.is_valid():
            equity = form.save(commit=False)
            equity.user = request.user
            equity.save()
            messages.success(request, f"'{equity.equity_name}' registered.")
            return redirect('manage_equity')
    else:
        form = EquityForm()
    return render(request, 'equity/add_equity.html', {'form': form})


@login_required
def edit_equity(request, pk):
    equity = get_object_or_404(Equity, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EquityForm(request.POST, instance=equity)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{equity.equity_name}' updated.")
            return redirect('manage_equity')
    else:
        form = EquityForm(instance=equity)
    return render(request, 'equity/add_equity.html', {'form': form, 'equity': equity, 'editing': True})


@login_required
def delete_equity(request, pk):
    equity = get_object_or_404(Equity, pk=pk, user=request.user)
    if request.method == 'POST':
        equity.delete()
        messages.success(request, "Equity record deleted.")
    return redirect('manage_equity')
