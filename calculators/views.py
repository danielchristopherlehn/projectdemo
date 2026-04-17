from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from projects.models import Project
from .models import LoanData, MortgageData, RentVsOwnData
from .calculations import calculate_loan, calculate_mortgage, calculate_rent_vs_own


@login_required
def loan_calculator_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    asset = project.linked_asset
    result = None

    saved = getattr(project, 'loan_data', None)
    form_data = {
        "principal": str(saved.principal) if saved else "",
        "rate":      str(saved.rate) if saved else "",
        "years":     str(saved.years) if saved else "",
    }

    if request.method == "POST":
        form_data = {k: request.POST.get(k, "") for k in form_data}
        try:
            principal = float(form_data["principal"] or 0)
            rate = float(form_data["rate"] or 0)
            years = int(form_data["years"] or 0)
            LoanData.objects.update_or_create(
                project=project,
                defaults={"principal": principal, "rate": rate, "years": years}
            )
            result = calculate_loan(principal, rate, years)
        except ValueError:
            result = {"error": "Please enter valid numbers in all fields."}

    return render(request, "calculators/loan.html", {
        "project": project,
        "asset": asset,
        "result": result,
        "form_data": form_data,
    })


@login_required
def mortgage_calculator_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    asset = project.linked_asset
    result = None

    saved = getattr(project, 'mortgage_data', None)
    if saved:
        form_data = {
            "price":        str(saved.price),
            "down_payment": str(saved.down_payment),
            "rate":         str(saved.rate),
            "years":        str(saved.years),
        }
    elif asset:
        form_data = {
            "price":        str(asset.value_estimate or asset.purchase_price),
            "down_payment": "",
            "rate":         "",
            "years":        "",
        }
    else:
        form_data = {"price": "", "down_payment": "", "rate": "", "years": ""}

    if request.method == "POST":
        form_data = {k: request.POST.get(k, "") for k in form_data}
        try:
            price = float(form_data["price"] or 0)
            down_payment = float(form_data["down_payment"] or 0)
            rate = float(form_data["rate"] or 0)
            years = int(form_data["years"] or 0)
            MortgageData.objects.update_or_create(
                project=project,
                defaults={"price": price, "down_payment": down_payment,
                          "rate": rate, "years": years}
            )
            result = calculate_mortgage(price, down_payment, rate, years)
        except ValueError:
            result = {"error": "Please enter valid numbers in all fields."}

    return render(request, "calculators/mortgage.html", {
        "project": project,
        "asset": asset,
        "result": result,
        "form_data": form_data,
    })


@login_required
def rent_vs_own_calculator_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    asset = project.linked_asset
    result = None

    saved = getattr(project, 'rent_vs_own_data', None)
    if saved:
        form_data = {
            "rent":          str(saved.rent),
            "rent_increase": str(saved.rent_increase),
            "price":         str(saved.price),
            "down_payment":  str(saved.down_payment),
            "rate":          str(saved.rate),
            "years":         "10",
        }
    elif asset:
        form_data = {
            "rent":          "",
            "rent_increase": "3.0",
            "price":         str(asset.value_estimate or asset.purchase_price),
            "down_payment":  "",
            "rate":          "",
            "years":         "10",
        }
    else:
        form_data = {
            "rent": "", "rent_increase": "", "price": "",
            "down_payment": "", "rate": "", "years": "10",
        }

    if request.method == "POST":
        form_data = {k: request.POST.get(k, "") for k in form_data}
        try:
            rent = float(form_data["rent"] or 0)
            rent_increase = float(form_data["rent_increase"] or 0)
            price = float(form_data["price"] or 0)
            down_payment = float(form_data["down_payment"] or 0)
            rate = float(form_data["rate"] or 0)
            years = int(form_data["years"] or 10)
            RentVsOwnData.objects.update_or_create(
                project=project,
                defaults={"rent": rent, "rent_increase": rent_increase,
                          "price": price, "down_payment": down_payment, "rate": rate}
            )
            result = calculate_rent_vs_own(
                rent, rent_increase, price, down_payment, rate, years)
        except ValueError:
            result = {"error": "Please enter valid numbers in all fields."}

    return render(request, "calculators/rent_vs_own.html", {
        "project": project,
        "asset": asset,
        "result": result,
        "form_data": form_data,
    })
