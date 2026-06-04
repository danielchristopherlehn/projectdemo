from django.db import models
from datetime import date


def current_year():
    return date.today().year


class LoanBASE(models.Model):
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    years = models.IntegerField(default=0)
    start_year = models.IntegerField(default=current_year)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def monthly_rate(self):
        return float((self.rate / 100) / 12)

    @property
    def total_months(self):
        return self.years * 12


class LoanData(LoanBASE):
    project = models.OneToOneField(
        "projects.Project", on_delete=models.CASCADE, related_name="loan_data")
    principal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Loan Data for {self.project.name}"


class MortgageData(LoanBASE):
    project = models.OneToOneField(
        "projects.Project", on_delete=models.CASCADE, related_name="mortgage_data")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    down_payment = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Mortgage Data for {self.project.name}"


class RentVsOwnData(LoanBASE):
    project = models.OneToOneField(
        "projects.Project", on_delete=models.CASCADE, related_name="rent_vs_own_data")
    rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rent_increase = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    down_payment = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Rent vs Own Data for {self.project.name}"
