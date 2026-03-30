# <-- Added get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from .models import Liability
from .forms import LiabilityForm


@login_required
def manage_liabilities(request):
    if request.method == 'POST':
        form = LiabilityForm(request.POST)
        if form.is_valid():
            liability = form.save(commit=False)
            liability.user = request.user
            liability.save()
            return redirect('manage_liabilities')
    else:
        form = LiabilityForm()

    # Get only THIS user's liabilities
    user_liabilities = Liability.objects.filter(user=request.user)

    # Math: Total Debt
    total_liability = user_liabilities.aggregate(Sum('principal_amount'))[
        'principal_amount__sum'] or 0

    # Math: For the HTML allocation bar
    type_counts = user_liabilities.values(
        'liability_type').annotate(total=Count('id'))

    context = {
        'form': form,
        'liabilities': user_liabilities,
        'total_liability': total_liability,
        'type_counts': type_counts,
    }
    return render(request, 'liabilities/manage_liabilities.html', context)

# -------------------------------------------------------------------
# NEW VIEWS FOR EDITING AND DELETING
# -------------------------------------------------------------------


@login_required
def edit_liability(request, pk):
    # This ensures a user can only edit THEIR OWN liabilities
    liability = get_object_or_404(Liability, pk=pk, user=request.user)

    if request.method == 'POST':
        form = LiabilityForm(request.POST, instance=liability)
        if form.is_valid():
            form.save()
            return redirect('manage_liabilities')
    else:
        form = LiabilityForm(instance=liability)

    return render(request, 'liabilities/edit_liability.html', {'form': form})


@login_required
def delete_liability(request, pk):
    # This ensures a user can only delete THEIR OWN liabilities
    liability = get_object_or_404(Liability, pk=pk, user=request.user)
    liability.delete()
    return redirect('manage_liabilities')
