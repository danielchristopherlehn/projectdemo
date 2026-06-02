import json
from dataclasses import asdict

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from assets.models import Asset
from budget.models import Account
from liabilities.models import Liability
from main.models import GlossaryTerm

from .models import ContactMessage
from .simulation import SimulationInput, run_simulation


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
        active_Status=True
    )

    investments = Asset.objects.filter(
        user=user,
        asset_type="Long-Term Investments",
        active_Status=True
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
        investments.aggregate(Sum("value_estimate"))["value_estimate__sum"] or 0
    )

    liquid_value = float(
        liquid_accounts.aggregate(Sum("initial_balance"))["initial_balance__sum"] or 0
    )

    total_debt = float(
        liabilities.aggregate(Sum("principal_amount"))["principal_amount__sum"] or 0
    )

    if liabilities.exists() and total_debt > 0:
        avg_rate = float(
            sum(
                float(liability.interest_rate) * float(liability.principal_amount)
                for liability in liabilities
            ) / total_debt
        )
    else:
        avg_rate = 5.0

    current_nw = property_value + investment_value + liquid_value - total_debt

    result = None

    form_data = {
        "horizon": 10,
        "property_drift": 4.0,
        "property_volatility": 8.0,
        "investment_drift": 7.0,
        "investment_volatility": 15.0,
        "inflation_rate": 2.5,
        "income_growth_rate": 3.0,
        "annual_income": 0,
        "savings_rate": 20.0,
    }

    if request.method == "POST":
        for key in form_data:
            try:
                form_data[key] = float(request.POST.get(key, form_data[key]))
            except (TypeError, ValueError):
                pass

        form_data["horizon"] = int(form_data["horizon"])

        simulation_input = SimulationInput(
            property_value=property_value,
            liquid_value=liquid_value,
            investment_value=investment_value,
            total_debt=total_debt,
            avg_interest_rate=avg_rate,
            **form_data,
        )

        result = run_simulation(simulation_input)

    context = {
        "property_value": property_value,
        "investment_value": investment_value,
        "liquid_value": liquid_value,
        "total_assets": property_value + investment_value + liquid_value,
        "total_debt": total_debt,
        "current_nw": current_nw,
        "properties": properties,
        "investments": investments,
        "liquid_accounts": liquid_accounts,
        "liabilities": liabilities,
        "form_data": form_data,
        "result": result,
        "result_json": json.dumps(asdict(result)) if result else "null",
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