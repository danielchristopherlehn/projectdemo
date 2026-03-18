from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import ProjectForm
from .models import Project

def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)

            if request.user.is_authenticated:
                project.user = request.user

            project.save()
            return redirect("dashboard")
    else:
        form = ProjectForm()

    return render(request, "projects/create_project.html", {"form": form})


# We use the next code lines to create a delete button right next to the old projects
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    return redirect("dashboard")


# First calculator: rent vs own
# Second calculator: mortgage
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.calculator_type == "mortgage":
        result = None

        form_data = {
            "price": "",
            "down_payment": "",
            "rate": "",
            "years": "",
        }

        if request.method == "POST":
            form_data["price"] = request.POST.get("price", "")
            form_data["down_payment"] = request.POST.get("down_payment", "")
            form_data["rate"] = request.POST.get("rate", "")
            form_data["years"] = request.POST.get("years", "")

            try:
                price = float(form_data["price"] or 0)
                down_payment = float(form_data["down_payment"] or 0)
                rate = float(form_data["rate"] or 0)
                years = int(form_data["years"] or 0)

                loan = max(price - down_payment, 0)
                monthly_rate = (rate / 100) / 12
                number_of_payments = years * 12

                if monthly_rate > 0 and number_of_payments > 0:
                    monthly_payment = loan * (
                        monthly_rate * (1 + monthly_rate) ** number_of_payments
                    ) / ((1 + monthly_rate) ** number_of_payments - 1)
                else:
                    monthly_payment = (
                        loan / number_of_payments if number_of_payments > 0 else 0
                    )

                total_paid = monthly_payment * number_of_payments
                total_interest = total_paid - loan

                result = {
                    "loan": round(loan, 2),
                    "monthly_payment": round(monthly_payment, 2),
                    "total_paid": round(total_paid, 2),
                    "total_interest": round(total_interest, 2),
                }

            except ValueError:
                result = {
                    "error": "Please enter valid numbers in all fields."
                }

        return render(
            request,
            "calculators/mortgage.html",
            {
                "project": project,
                "result": result,
                "form_data": form_data,
            },
        )

    if project.calculator_type == "rent_vs_own":
        result = None

        form_data = {
            "rent": "",
            "rent_increase": "",
            "price": "",
            "down_payment": "",
            "rate": "",
        }

        if request.method == "POST":
            form_data["rent"] = request.POST.get("rent", "")
            form_data["rent_increase"] = request.POST.get("rent_increase", "")
            form_data["price"] = request.POST.get("price", "")
            form_data["down_payment"] = request.POST.get("down_payment", "")
            form_data["rate"] = request.POST.get("rate", "")

            try:
                rent = float(form_data["rent"] or 0)
                rent_increase = float(form_data["rent_increase"] or 0)
                price = float(form_data["price"] or 0)
                down_payment = float(form_data["down_payment"] or 0)
                rate = float(form_data["rate"] or 0)

                years = 10

                total_rent = 0
                current_rent = rent

                for _ in range(years):
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
                    monthly_payment = (
                        loan / number_of_payments if number_of_payments > 0 else 0
                    )

                total_buy_cost = down_payment + (monthly_payment * number_of_payments)

                result = {
                    "rent_cost": round(total_rent, 2),
                    "buy_cost": round(total_buy_cost, 2),
                    "monthly_payment": round(monthly_payment, 2),
                }

            except ValueError:
                result = {
                    "error": "Please enter valid numbers in all fields."
                }

        return render(
            request,
            "calculators/rent_vs_own.html",
            {
                "project": project,
                "result": result,
                "form_data": form_data,
            },
        )

    return render(request, "projects/project_detail.html", {"project": project})