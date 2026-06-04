# Pure calculation logic — no Django imports here.
# All database access lives in services.py.

# Financial rules used across the advice engine.
PMI_DOWN_PAYMENT_MIN = 20
DTI_HEALTHY_LIMIT = 36
DTI_STRETCHED_LIMIT = 43
RENT_COMFORTABLE_LIMIT = 30
RENT_STRETCHED_LIMIT = 40


def build_schedule(starting_balance, monthly_rate, monthly_payment, years, start_year):
    # Builds the year-by-year amortization table.
    # start_year turns row numbers into real calendar years (2025, 2026 …).
    schedule = []
    balance = starting_balance

    for year in range(1, years + 1):
        interest_year = 0
        principal_year = 0

        for month in range(12):
            if balance <= 0:
                break
            interest = balance * monthly_rate
            principal_paid = monthly_payment - interest
            balance -= principal_paid
            interest_year += interest
            principal_year += principal_paid

        schedule.append({
            "year": year,
            "calendar_year": start_year + year - 1,
            "principal_paid": round(principal_year, 2),
            "interest_paid": round(interest_year, 2),
            "balance": round(max(balance, 0), 2),
        })

    return schedule


class Loan:
    def __init__(self, principal, rate, years, start_year):
        self.principal = principal
        self.rate = rate
        self.years = years
        self.start_year = start_year

    @property
    def monthly_rate(self):
        return (self.rate / 100) / 12

    @property
    def total_months(self):
        return self.years * 12

    @property
    def monthly_payment(self):
        # Standard annuity formula. Guard against zero term or zero rate.
        if self.monthly_rate > 0 and self.total_months > 0:
            r = self.monthly_rate
            n = self.total_months
            return self.principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        return self.principal / self.total_months if self.total_months > 0 else 0

    @property
    def total_payment(self):
        return self.monthly_payment * self.total_months

    @property
    def total_interest(self):
        return self.total_payment - self.principal

    @property
    def schedule(self):
        return build_schedule(
            self.principal, self.monthly_rate,
            self.monthly_payment, self.years, self.start_year
        )


class Mortgage(Loan):
    # A mortgage is a loan for (price - down_payment).
    def __init__(self, price, down_payment, rate, years, start_year):
        self.price = price
        self.down_payment = down_payment
        loan_amount = price - down_payment
        super().__init__(loan_amount, rate, years, start_year)
        self.loan_amount = self.principal


def build_advice(rent, price, down_payment, monthly_mortgage, monthly_income, monthly_debt):
    advice = []

    if price > 0:
        down_pct = (down_payment / price) * 100
        if down_pct >= PMI_DOWN_PAYMENT_MIN:
            advice.append({
                "level": "good",
                "title": "Down Payment: Strong",
                "message": f"Your down payment is {down_pct:.0f}%. You avoid PMI.",
            })
        else:
            advice.append({
                "level": "warning",
                "title": "Down Payment: Below 20%",
                "message": (
                    f"Your down payment is only {down_pct:.0f}%. "
                    "Lenders usually require PMI, adding to monthly costs."
                ),
            })

    if monthly_income > 0:
        dti = ((monthly_debt + monthly_mortgage) / monthly_income) * 100
        if dti < DTI_HEALTHY_LIMIT:
            advice.append({
                "level": "good",
                "title": f"Debt-to-Income: Healthy ({dti:.0f}%)",
                "message": f"DTI below {DTI_HEALTHY_LIMIT}%. Lenders consider this healthy.",
            })
        elif dti < DTI_STRETCHED_LIMIT:
            advice.append({
                "level": "warning",
                "title": f"Debt-to-Income: Stretched ({dti:.0f}%)",
                "message": (
                    f"DTI between {DTI_HEALTHY_LIMIT}% and {DTI_STRETCHED_LIMIT}%. "
                    "Lenders will look closely."
                ),
            })
        else:
            advice.append({
                "level": "danger",
                "title": f"Debt-to-Income: High Risk ({dti:.0f}%)",
                "message": (
                    f"DTI exceeds {DTI_STRETCHED_LIMIT}%. "
                    "High risk of rejection or becoming house poor."
                ),
            })

    if monthly_income > 0 and rent > 0:
        rent_ratio = (rent / monthly_income) * 100
        if rent_ratio <= RENT_COMFORTABLE_LIMIT:
            advice.append({
                "level": "good",
                "title": f"Rent Affordability: Comfortable ({rent_ratio:.0f}%)",
                "message": f"Rent is within the {RENT_COMFORTABLE_LIMIT}% rule.",
            })
        elif rent_ratio <= RENT_STRETCHED_LIMIT:
            advice.append({
                "level": "warning",
                "title": f"Rent Affordability: Stretched ({rent_ratio:.0f}%)",
                "message": f"Rent exceeds {RENT_COMFORTABLE_LIMIT}% of income. Less room for savings.",
            })
        else:
            advice.append({
                "level": "danger",
                "title": f"Rent Affordability: Very High ({rent_ratio:.0f}%)",
                "message": f"Rent exceeds {RENT_STRETCHED_LIMIT}% of income. Significant burden.",
            })

    return advice


class RentVsOwnResult:
    def __init__(self, rent, rent_increase, price, down_payment, rate, years,
                 monthly_income=0, monthly_debt=0, start_year=None):
        self.years = years

        mortgage = Mortgage(price, down_payment, rate, years, start_year or 0)
        self.monthly_mortgage = mortgage.monthly_payment

        self.total_own_cost = down_payment + (self.monthly_mortgage * years * 12)

        # Compound rent increases year by year.
        self.total_rent_cost = 0
        current_rent = rent
        for _ in range(years):
            self.total_rent_cost += current_rent * 12
            current_rent *= (1 + rent_increase / 100)

        self.verdict = (
            "Buying is cheaper" if self.total_own_cost < self.total_rent_cost
            else "Renting is cheaper"
        )

        self.advice = build_advice(
            rent, price, down_payment, self.monthly_mortgage,
            monthly_income, monthly_debt
        )
