from django.db import migrations


def seed_glossary_terms(apps, schema_editor):
    GlossaryTerm = apps.get_model("main", "GlossaryTerm")

    glossary_terms = [
        {
            "term_type": "loan",
            "term": "Principal",
            "slug": "principal",
            "definition": "Principal is the original amount borrowed before interest and other charges are added.",
        },
        {
            "term_type": "loan",
            "term": "Interest Rate",
            "slug": "interest-rate",
            "definition": "The interest rate is the percentage charged by the lender for borrowing money, usually shown as a yearly rate.",
        },
        {
            "term_type": "loan",
            "term": "Loan Term",
            "slug": "loan-term",
            "definition": "Loan term is the total length of time you have to repay the loan, often measured in years.",
        },
        {
            "term_type": "loan",
            "term": "Monthly Payment",
            "slug": "monthly-payment",
            "definition": "Monthly payment is the amount paid every month to gradually repay a loan, including principal and interest when applicable.",
        },
        {
            "term_type": "loan",
            "term": "Total Interest",
            "slug": "total-interest",
            "definition": "Total interest is the full amount paid to the lender on top of the original borrowed amount over the entire repayment period.",
        },
        {
            "term_type": "mortgage",
            "term": "Mortgage",
            "slug": "mortgage",
            "definition": "A mortgage is a loan used to buy property, where the property itself usually serves as security for the lender.",
        },
        {
            "term_type": "mortgage",
            "term": "House Price",
            "slug": "house-price",
            "definition": "House price is the total purchase price of the property before subtracting the down payment.",
        },
        {
            "term_type": "mortgage",
            "term": "Down Payment",
            "slug": "down-payment",
            "definition": "A down payment is the upfront amount paid by the buyer, reducing the amount that must be financed with a loan.",
        },
        {
            "term_type": "housing",
            "term": "Monthly Rent",
            "slug": "monthly-rent",
            "definition": "Monthly rent is the recurring amount paid each month to live in a property owned by someone else.",
        },
        {
            "term_type": "housing",
            "term": "Rent Increase",
            "slug": "rent-increase",
            "definition": "Rent increase is the expected percentage by which the rent may rise over time, usually each year.",
        },
        {
            "term_type": "housing",
            "term": "Total Rent Cost",
            "slug": "total-rent-cost",
            "definition": "Total rent cost is the full amount spent on rent across the comparison period, including any increases over time.",
        },
        {
            "term_type": "housing",
            "term": "Total Buy Cost",
            "slug": "total-buy-cost",
            "definition": "Total buy cost is the overall cost of purchasing over the comparison period, often including the down payment and mortgage payments.",
        },
        {
            "term_type": "budget",
            "term": "Monthly Income",
            "slug": "monthly-income",
            "definition": "Monthly income is the money received during a typical month from salary, freelance work, benefits, or other sources.",
        },
        {
            "term_type": "budget",
            "term": "Utilities",
            "slug": "utilities",
            "definition": "Utilities are essential household service costs such as electricity, water, heating, internet, and similar recurring bills.",
        },
        {
            "term_type": "budget",
            "term": "Total Expenses",
            "slug": "total-expenses",
            "definition": "Total expenses are the combined costs of all spending categories during the selected period.",
        },
        {
            "term_type": "budget",
            "term": "Monthly Savings",
            "slug": "monthly-savings",
            "definition": "Monthly savings are the amount left after subtracting total monthly expenses from monthly income.",
        },
        {
            "term_type": "budget",
            "term": "Yearly Savings",
            "slug": "yearly-savings",
            "definition": "Yearly savings are the projected savings over a full year based on the monthly savings figure.",
        },
    ]

    for item in glossary_terms:
        GlossaryTerm.objects.update_or_create(slug=item["slug"], defaults=item)


def remove_glossary_terms(apps, schema_editor):
    GlossaryTerm = apps.get_model("main", "GlossaryTerm")
    GlossaryTerm.objects.filter(
        slug__in=[
            "principal",
            "interest-rate",
            "loan-term",
            "monthly-payment",
            "total-interest",
            "mortgage",
            "house-price",
            "down-payment",
            "monthly-rent",
            "rent-increase",
            "total-rent-cost",
            "total-buy-cost",
            "monthly-income",
            "utilities",
            "total-expenses",
            "monthly-savings",
            "yearly-savings",
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_glossary_terms, remove_glossary_terms),
    ]
