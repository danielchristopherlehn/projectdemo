from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProjectForm
from .models import Project


def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect("dashboard")
    else:
        form = ProjectForm()

    return render(request, "projects/create_project.html", {"form": form})


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.calculator_type == "rent_vs_own":
        result = None

        if request.method == "POST":
            rent = float(request.POST.get("rent") or 0)
            rent_increase = float(request.POST.get("rent_increase") or 0)
            price = float(request.POST.get("price") or 0)
            down_payment = float(request.POST.get("down_payment") or 0)
            rate = float(request.POST.get("rate") or 0)

            years = 10

            total_rent = 0
            current_rent = rent

            for year in range(years):
                total_rent += current_rent * 12
                current_rent *= (1 + rent_increase / 100)

            loan = max(price - down_payment, 0)
            monthly_rate = (rate / 100) / 12
            number_of_payments = years * 12

            if monthly_rate > 0 and loan > 0:
                monthly_payment = loan * (
                    monthly_rate * (1 + monthly_rate) ** number_of_payments
                ) / ((1 + monthly_rate) ** number_of_payments - 1)
            else:
                monthly_payment = loan / number_of_payments if number_of_payments > 0 else 0

            total_buy_cost = down_payment + (monthly_payment * number_of_payments)

            result = {
                "rent_cost": round(total_rent, 2),
                "buy_cost": round(total_buy_cost, 2),
                "monthly_payment": round(monthly_payment, 2),
            }

        return render(
            request,
            "calculators/rent_vs_own.html",
            {
                "project": project,
                "result": result,
            },
        )

    return render(request, "projects/project_detail.html", {"project": project})