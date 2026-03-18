from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import ProjectForm
from .models import Project

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


# Delete project
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    return redirect("dashboard")


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)


    # First calculator: Loan
  
    if project.calculator_type == "loan":
        result = None

        form_data = {
            "principal": "",
            "rate": "",
            "years": "",
        }

        if request.method == "POST":
            form_data["principal"] = request.POST.get("principal", "")
            form_data["rate"] = request.POST.get("rate", "")
            form_data["years"] = request.POST.get("years", "")

            try:
                principal = float(form_data["principal"] or 0)
                rate = float(form_data["rate"] or 0)
                years = int(form_data["years"] or 0)

                monthly_rate = (rate / 100) / 12
                number_of_payments = years * 12

                if monthly_rate > 0 and number_of_payments > 0:
                    monthly_payment = principal * (
                        monthly_rate * (1 + monthly_rate) ** number_of_payments
                    ) / ((1 + monthly_rate) ** number_of_payments - 1)
                else:
                    monthly_payment = (
                        principal / number_of_payments if number_of_payments > 0 else 0
                    )

                total_paid = monthly_payment * number_of_payments
                total_interest = total_paid - principal

                result = {
                    "principal": round(principal, 2),
                    "monthly_payment": round(monthly_payment, 2),
                    "total_paid": round(total_paid, 2),
                    "total_interest": round(total_interest, 2),
                }

            except ValueError:
                result = {"error": "Please enter valid numbers in all fields."}

        return render(
            request,
            "calculators/loan.html",
            {
                "project": project,
                "result": result,
                "form_data": form_data,
            },
        )

   
 
    # Second calculator: Personal Budget 

    if project.calculator_type == "budget":
        result = None

        form_data = {
            "income": "",
            "housing": "",
            "food": "",
            "transport": "",
            "utilities": "",
            "other": "",
        }

        if request.method == "POST":
            form_data["income"] = request.POST.get("income", "")
            form_data["housing"] = request.POST.get("housing", "")
            form_data["food"] = request.POST.get("food", "")
            form_data["transport"] = request.POST.get("transport", "")
            form_data["utilities"] = request.POST.get("utilities", "")
            form_data["other"] = request.POST.get("other", "")

            try:
                income = float(form_data["income"] or 0)
                housing = float(form_data["housing"] or 0)
                food = float(form_data["food"] or 0)
                transport = float(form_data["transport"] or 0)
                utilities = float(form_data["utilities"] or 0)
                other = float(form_data["other"] or 0)

                total_expenses = housing + food + transport + utilities + other
                monthly_savings = income - total_expenses
                yearly_savings = monthly_savings * 12

                result = {
                    "income": round(income, 2),
                    "total_expenses": round(total_expenses, 2),
                    "monthly_savings": round(monthly_savings, 2),
                    "yearly_savings": round(yearly_savings, 2),
                }

            except ValueError:
                result = {
                    "error": "Please enter valid numbers in all fields."
                }

        return render(
            request,
            "calculators/budget.html",
            {
                "project": project,
                "result": result,
                "form_data": form_data,
            },
        )
  # Third calculator: Mortgage
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
                result = {"error": "Please enter valid numbers in all fields."}

        return render(
            request,
            "calculators/mortgage.html",
            {
                "project": project,
                "result": result,
                "form_data": form_data,
            },
        )

 
    # Fourth calculator: Rent vs Own
   
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
                result = {"error": "Please enter valid numbers in all fields."}

        return render(
            request,
            "calculators/rent_vs_own.html",
            {
                "project": project,
                "result": result,
                "form_data": form_data,
            },
        )
    
    
  
    # Default fallback
 
    return render(request, "projects/project_detail.html", {"project": project})