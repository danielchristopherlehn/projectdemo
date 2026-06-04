# Services layer: DB queries and result object construction.
# Views call these functions instead of doing the work themselves.
from django.db.models import Sum, Min, Max

from budget.models import Transaction
from liabilities.models import Liability
from .calculations import Loan, Mortgage, RentVsOwnResult


def get_monthly_income(user):
    # Average monthly revenue across all the user's recorded transactions.
    txns = Transaction.objects.filter(user=user)
    total = float(
        txns.filter(transaction_type="REVENUE")
        .aggregate(Sum("amount"))["amount__sum"] or 0
    )
    span = txns.aggregate(first=Min("date"), last=Max("date"))
    first, last = span["first"], span["last"]
    if first and last:
        months = (last.year - first.year) * 12 + (last.month - first.month) + 1
    else:
        months = 1
    return total / months


def get_monthly_debt(user):
    # Total monthly liability payments registered by the user.
    total = Liability.objects.filter(user=user).aggregate(
        Sum("monthly_payment"))["monthly_payment__sum"]
    return float(total or 0)


def build_loan_result(saved):
    if not saved:
        return None
    return Loan(
        principal=float(saved.principal),
        rate=float(saved.rate),
        years=int(saved.years),
        start_year=int(saved.start_year),
    )


def build_mortgage_result(saved):
    if not saved:
        return None
    return Mortgage(
        price=float(saved.price),
        down_payment=float(saved.down_payment),
        rate=float(saved.rate),
        years=int(saved.years),
        start_year=int(saved.start_year),
    )


def build_rent_vs_own_result(saved, user):
    if not saved:
        return None
    return RentVsOwnResult(
        rent=float(saved.rent),
        rent_increase=float(saved.rent_increase),
        price=float(saved.price),
        down_payment=float(saved.down_payment),
        rate=float(saved.rate),
        years=int(saved.years),
        monthly_income=get_monthly_income(user),
        monthly_debt=get_monthly_debt(user),
        start_year=int(saved.start_year),
    )
