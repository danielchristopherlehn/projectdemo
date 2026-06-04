from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from projects.models import Project
from .forms import LoanDataForm, MortgageDataForm, RentVsOwnDataForm
from .services import build_loan_result, build_mortgage_result, build_rent_vs_own_result


@login_required
def loan_calculator_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    saved = getattr(project, 'loan_data', None)

    if request.method == "POST":
        form = LoanDataForm(request.POST, instance=saved)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.project = project
            saved.save()
    else:
        form = LoanDataForm(instance=saved)

    return render(request, "calculators/loan.html", {
        "project": project,
        "asset": project.linked_asset,
        "form": form,
        "result": build_loan_result(saved),
        "saved": saved,
    })


@login_required
def mortgage_calculator_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    saved = getattr(project, 'mortgage_data', None)

    if request.method == "POST":
        form = MortgageDataForm(request.POST, instance=saved)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.project = project
            saved.save()
    else:
        initial = {}
        if not saved and project.linked_asset:
            initial['price'] = (
                project.linked_asset.value_estimate or project.linked_asset.purchase_price
            )
        form = MortgageDataForm(instance=saved, initial=initial)

    return render(request, "calculators/mortgage.html", {
        "project": project,
        "asset": project.linked_asset,
        "form": form,
        "result": build_mortgage_result(saved),
        "saved": saved,
    })


@login_required
def rent_vs_own_calculator_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    saved = getattr(project, 'rent_vs_own_data', None)

    if request.method == "POST":
        form = RentVsOwnDataForm(request.POST, instance=saved)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.project = project
            saved.save()
    else:
        initial = {'years': 10, 'rent_increase': 3.0}
        if not saved and project.linked_asset:
            initial['price'] = (
                project.linked_asset.value_estimate or project.linked_asset.purchase_price
            )
        form = RentVsOwnDataForm(instance=saved, initial=initial)

    return render(request, "calculators/rent_vs_own.html", {
        "project": project,
        "asset": project.linked_asset,
        "form": form,
        "result": build_rent_vs_own_result(saved, request.user),
        "saved": saved,
    })
