from django.db import models


class LoanData(models.Model):
    project = models.OneToOneField(
        "projects.Project", on_delete=models.CASCADE, related_name="loan_data")
    principal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    years = models.IntegerField(default=0)

    def __str__(self):
        return f"Loan Data for {self.project.name}"


class MortgageData(models.Model):
    project = models.OneToOneField(
        "projects.Project", on_delete=models.CASCADE, related_name="mortgage_data")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    down_payment = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    years = models.IntegerField(default=0)

    def __str__(self):
        return f"Mortgage Data for {self.project.name}"


class RentVsOwnData(models.Model):
    project = models.OneToOneField(
        "projects.Project", on_delete=models.CASCADE, related_name="rent_vs_own_data")
    rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rent_increase = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    down_payment = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"Rent vs Own Data for {self.project.name}"
