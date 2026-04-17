from dataclasses import dataclass
from typing import Optional


# --- LOAN ---

@dataclass
class LoanResult:
    principal: float
    monthly_payment: float
    total_paid: float
    total_interest: float
    error: Optional[str] = None


def calculate_loan(principal: float, rate: float, years: int) -> LoanResult:
    try:
        monthly_rate = (rate / 100) / 12
        n = years * 12

        if monthly_rate > 0 and n > 0:
            monthly_payment = principal * (
                monthly_rate * (1 + monthly_rate) ** n
            ) / ((1 + monthly_rate) ** n - 1)
        elif n > 0:
            monthly_payment = principal / n
        else:
            monthly_payment = 0

        total_paid = monthly_payment * n
        total_interest = total_paid - principal

        return LoanResult(
            principal=round(principal, 2),
            monthly_payment=round(monthly_payment, 2),
            total_paid=round(total_paid, 2),
            total_interest=round(total_interest, 2),
        )
    except Exception as e:
        return LoanResult(0, 0, 0, 0, error=str(e))


# --- MORTGAGE ---

@dataclass
class MortgageResult:
    loan_amount: float
    monthly_payment: float
    total_paid: float
    total_interest: float
    error: Optional[str] = None


def calculate_mortgage(price: float, down_payment: float, rate: float, years: int) -> MortgageResult:
    try:
        loan_amount = price - down_payment
        monthly_rate = (rate / 100) / 12
        n = years * 12

        if monthly_rate > 0 and n > 0:
            monthly_payment = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** n
            ) / ((1 + monthly_rate) ** n - 1)
        elif n > 0:
            monthly_payment = loan_amount / n
        else:
            monthly_payment = 0

        total_paid = monthly_payment * n
        total_interest = total_paid - loan_amount

        return MortgageResult(
            loan_amount=round(loan_amount, 2),
            monthly_payment=round(monthly_payment, 2),
            total_paid=round(total_paid, 2),
            total_interest=round(total_interest, 2),
        )
    except Exception as e:
        return MortgageResult(0, 0, 0, 0, error=str(e))


# --- RENT VS OWN ---

@dataclass
class RentVsOwnResult:
    years: int
    total_rent_cost: float
    total_own_cost: float
    monthly_mortgage: float
    verdict: str          # "renting" | "buying" | "similar"
    error: Optional[str] = None


def calculate_rent_vs_own(
    rent: float,
    rent_increase: float,   # annual % e.g. 3.0
    price: float,
    down_payment: float,
    rate: float,
    years: int = 10,
) -> RentVsOwnResult:
    try:
        # Mortgage side
        loan_amount = price - down_payment
        monthly_rate = (rate / 100) / 12
        n = years * 12

        if monthly_rate > 0 and n > 0:
            monthly_mortgage = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** n
            ) / ((1 + monthly_rate) ** n - 1)
        elif n > 0:
            monthly_mortgage = loan_amount / n
        else:
            monthly_mortgage = 0

        total_own_cost = down_payment + (monthly_mortgage * n)

        # Rent side — compound rent increases annually
        total_rent_cost = 0.0
        monthly_rent = rent
        for year in range(years):
            total_rent_cost += monthly_rent * 12
            monthly_rent *= (1 + rent_increase / 100)

        diff = total_own_cost - total_rent_cost
        if abs(diff) < total_own_cost * 0.02:   # within 2%
            verdict = "similar"
        elif diff > 0:
            verdict = "renting"
        else:
            verdict = "buying"

        return RentVsOwnResult(
            years=years,
            total_rent_cost=round(total_rent_cost, 2),
            total_own_cost=round(total_own_cost, 2),
            monthly_mortgage=round(monthly_mortgage, 2),
            verdict=verdict,
        )
    except Exception as e:
        return RentVsOwnResult(0, 0, 0, 0, "", error=str(e))
