from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum

# Import your models
from projects.models import Project
from assets.models import Asset
from liabilities.models import Liability
from equity.models import Equity


@login_required
def dashboard(request):
    user = request.user

    # 1. Fetch Projects
    projects = Project.objects.filter(user=user).order_by("-created_at")

    # 2. Calculate Totals (Using your specific model field names)
    # Using 'value_estimate' based on your Error choices
    total_assets = Asset.objects.filter(user=user).aggregate(
        Sum('value_estimate')
    )['value_estimate__sum'] or 0

    # Using 'principal_amount' (Standard for your setup)
    total_liabilities = Liability.objects.filter(user=user).aggregate(
        Sum('principal_amount')
    )['principal_amount__sum'] or 0

    # Using 'amount' for Equity
    total_equity = Equity.objects.filter(user=user).aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    # 3. Accounting Logic
    right_side_total = total_liabilities + total_equity
    is_balanced = (total_assets == right_side_total)
    net_worth = total_assets - total_liabilities

    context = {
        'projects': projects,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'right_side_total': right_side_total,
        'is_balanced': is_balanced,
        'net_worth': net_worth,
    }

    return render(request, "dashboard/dashboard.html", context)
