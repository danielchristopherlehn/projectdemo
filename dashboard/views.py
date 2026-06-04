from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Min, Max
from django.shortcuts import render

from assets.models import Asset
from budget.models import Account, Transaction
from liabilities.models import Liability
from equity.models import Equity
from main.models import GlossaryTerm

from .models import ContactMessage


def landing_page(request):
    return render(request, "landing.html")


@login_required
def dashboard(request):
    return render(request, "dashboard/dashboard.html")


@login_required
def glossary(request):
    terms = GlossaryTerm.objects.all().order_by("term_type", "term")

    return render(
        request,
        "dashboard/glossary.html",
        {"terms": terms}
    )


@login_required
def net_worth_summary(request):
    user = request.user

    properties = Asset.objects.filter(
        user=user,
        asset_type="Property & Land",
        active_status=True
    )

    investments = Asset.objects.filter(
        user=user,
        asset_type="Long-Term Investments",
        active_status=True
    )

    liquid_accounts = Account.objects.filter(
        user=user,
        account_class="CURRENT_ASSET"
    )

    liabilities = Liability.objects.filter(user=user)

    property_value = float(
        properties.aggregate(Sum("value_estimate"))["value_estimate__sum"] or 0
    )

    investment_value = float(
        investments.aggregate(Sum("value_estimate"))[
            "value_estimate__sum"] or 0
    )

    liquid_value = float(
        liquid_accounts.aggregate(Sum("initial_balance"))[
            "initial_balance__sum"] or 0
    )

    total_debt = float(
        liabilities.aggregate(Sum("principal_amount"))[
            "principal_amount__sum"] or 0
    )

    current_nw = property_value + investment_value + liquid_value - total_debt

    # Equity the user has manually logged in the Equity module.
    # In accounting, Equity = Assets - Liabilities, so current_nw above is the
    # "implied" equity. The reported figure is what the user actually itemised,
    # so the two usually differ and we show the gap instead of forcing a match.
    equity_records = Equity.objects.filter(user=user)
    reported_equity = float(
        equity_records.aggregate(Sum("amount"))["amount__sum"] or 0
    )
    equity_gap = current_nw - reported_equity

    transactions = Transaction.objects.filter(user=user)

    total_revenue = float(
        transactions.filter(transaction_type="REVENUE")
        .aggregate(Sum("amount"))["amount__sum"] or 0
    )
    total_expense = float(
        transactions.filter(transaction_type="EXPENSE")
        .aggregate(Sum("amount"))["amount__sum"] or 0
    )

    date_range = transactions.aggregate(first=Min("date"), last=Max("date"))
    first_date = date_range["first"]
    last_date = date_range["last"]
    if first_date and last_date:
        months = ((last_date.year - first_date.year) * 12
                  + (last_date.month - first_date.month) + 1)
    else:
        months = 1

    avg_monthly_income = total_revenue / months
    avg_yearly_income = avg_monthly_income * 12
    avg_monthly_expense = total_expense / months
    adjusted_income = avg_monthly_income - avg_monthly_expense

    context = {
        "property_value": property_value,
        "investment_value": investment_value,
        "liquid_value": liquid_value,
        "total_assets": property_value + investment_value + liquid_value,
        "total_debt": total_debt,
        "current_nw": current_nw,
        "reported_equity": reported_equity,
        "equity_gap": equity_gap,
        "equity_count": equity_records.count(),
        "properties": properties,
        "investments": investments,
        "liquid_accounts": liquid_accounts,
        "liabilities": liabilities,
        "avg_monthly_income": avg_monthly_income,
        "avg_yearly_income": avg_yearly_income,
        "adjusted_income": adjusted_income,
    }

    return render(request, "dashboard/net_worth_summary.html", context)


@login_required
def contact_us(request):
    success = False

    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            message=request.POST.get("message"),
        )

        success = True

    return render(request, "dashboard/contact.html", {"success": success})
