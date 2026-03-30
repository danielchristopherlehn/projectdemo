from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from .models import Equity
from .forms import EquityForm


@login_required
def manage_equity(request):
    if request.method == 'POST':
        form = EquityForm(request.POST)
        if form.is_valid():
            equity = form.save(commit=False)
            equity.user = request.user
            equity.save()
            return redirect('manage_equity')
    else:
        form = EquityForm()

    user_equity = Equity.objects.filter(user=request.user)
    total_equity = user_equity.aggregate(Sum('amount'))['amount__sum'] or 0
    type_counts = user_equity.values('equity_type').annotate(total=Count('id'))

    context = {
        'form': form,
        'equities': user_equity,
        'total_equity': total_equity,
        'type_counts': type_counts,
    }
    return render(request, 'equity/manage_equity.html', context)


@login_required
def edit_equity(request, pk):
    equity = get_object_or_404(Equity, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EquityForm(request.POST, instance=equity)
        if form.is_valid():
            form.save()
            return redirect('manage_equity')
    else:
        form = EquityForm(instance=equity)
    return render(request, 'equity/edit_equity.html', {'form': form})


@login_required
def delete_equity(request, pk):
    equity = get_object_or_404(Equity, pk=pk, user=request.user)
    equity.delete()
    return redirect('manage_equity')
