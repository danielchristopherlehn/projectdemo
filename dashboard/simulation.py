import numpy as np
from dataclasses import dataclass
from typing import List


@dataclass
class SimulationInput:
    # Assets
    property_value: float        # total Property & Land value estimate
    liquid_value: float          # total bank + cash balance
    investment_value: float      # long-term investments value estimate

    # Liabilities
    total_debt: float            # total principal across all liabilities
    avg_interest_rate: float     # weighted average interest rate (e.g. 5.5)

    # Income
    annual_income: float         # current gross annual income
    income_growth_rate: float    # expected annual % salary growth (e.g. 3.0)

    # User-controlled assumptions
    horizon: int                 # years (5, 10, 20)
    # expected annual property appreciation % (e.g. 4.0)
    property_drift: float
    property_volatility: float   # annual volatility % (e.g. 8.0)
    # expected annual return % on investments (e.g. 7.0)
    investment_drift: float
    investment_volatility: float  # annual volatility % (e.g. 15.0)
    inflation_rate: float        # annual inflation % (e.g. 2.5)
    # % of income saved/invested annually (e.g. 20.0)
    savings_rate: float

    n_paths: int = 1000          # Monte Carlo paths


@dataclass
class SimulationResult:
    years: List[int]
    median: List[float]
    p10: List[float]             # pessimistic (10th percentile)
    p90: List[float]             # optimistic (90th percentile)
    p25: List[float]
    p75: List[float]

    # Summary table
    net_worth_year5: dict        # {median, p10, p90}
    net_worth_year10: dict
    net_worth_final: dict

    # Probability statements
    prob_statements: List[dict]  # [{threshold, probability, label}]

    # Current snapshot
    current_net_worth: float


def run_simulation(inp: SimulationInput) -> SimulationResult:
    np.random.seed(None)  # fresh seed each run
    dt = 1.0              # annual steps
    n = inp.horizon
    N = inp.n_paths

    # --- Convert percentages to decimals ---
    mu_prop = inp.property_drift / 100
    sig_prop = inp.property_volatility / 100
    mu_inv = inp.investment_drift / 100
    sig_inv = inp.investment_volatility / 100
    inflation = inp.inflation_rate / 100
    income_g = inp.income_growth_rate / 100
    interest = inp.avg_interest_rate / 100
    savings_r = inp.savings_rate / 100

    # --- Initial net worth ---
    current_nw = (inp.property_value + inp.liquid_value +
                  inp.investment_value - inp.total_debt)

    # --- Simulate paths: shape (N, n+1) ---
    # Property: GBM
    prop_paths = np.zeros((N, n + 1))
    prop_paths[:, 0] = inp.property_value
    prop_noise = np.random.normal(0, 1, (N, n))
    for t in range(1, n + 1):
        prop_paths[:, t] = prop_paths[:, t-1] * np.exp(
            (mu_prop - 0.5 * sig_prop**2) * dt +
            sig_prop * np.sqrt(dt) * prop_noise[:, t-1]
        )

    # Investments: GBM (martingale drift under risk-neutral: mu - 0.5*sigma^2)
    inv_paths = np.zeros((N, n + 1))
    inv_paths[:, 0] = inp.investment_value
    inv_noise = np.random.normal(0, 1, (N, n))
    for t in range(1, n + 1):
        inv_paths[:, t] = inv_paths[:, t-1] * np.exp(
            (mu_inv - 0.5 * sig_inv**2) * dt +
            sig_inv * np.sqrt(dt) * inv_noise[:, t-1]
        )

    # Liquid assets: deterministic growth at inflation rate
    liquid_paths = np.zeros((N, n + 1))
    liquid_paths[:, 0] = inp.liquid_value
    for t in range(1, n + 1):
        liquid_paths[:, t] = liquid_paths[:, t-1] * (1 + inflation)

    # Debt: amortises at avg interest rate (simple linear paydown + interest)
    debt_paths = np.zeros((N, n + 1))
    debt_paths[:, 0] = inp.total_debt
    for t in range(1, n + 1):
        remaining = max(debt_paths[:, t-1] - debt_paths[:, t-1] / max(n, 1), 0)
        debt_paths[:, t] = remaining

    # Income savings: deterministic (added to liquid each year)
    annual_income = inp.annual_income
    for t in range(1, n + 1):
        savings = annual_income * savings_r
        liquid_paths[:, t] += savings
        annual_income *= (1 + income_g)

    # --- Net worth paths ---
    nw_paths = (prop_paths + inv_paths + liquid_paths - debt_paths)

    # --- Extract percentiles ---
    years = list(range(n + 1))
    p10 = np.percentile(nw_paths, 10,  axis=0).tolist()
    p25 = np.percentile(nw_paths, 25,  axis=0).tolist()
    p50 = np.percentile(nw_paths, 50,  axis=0).tolist()
    p75 = np.percentile(nw_paths, 75,  axis=0).tolist()
    p90 = np.percentile(nw_paths, 90,  axis=0).tolist()

    def summary_at(year):
        if year > n:
            year = n
        col = nw_paths[:, year]
        return {
            'median': round(float(np.percentile(col, 50)), 0),
            'p10':    round(float(np.percentile(col, 10)), 0),
            'p90':    round(float(np.percentile(col, 90)), 0),
        }

    # --- Probability statements ---
    final_col = nw_paths[:, -1]
    thresholds = _smart_thresholds(current_nw, p90[-1])
    prob_statements = []
    for t in thresholds:
        prob = float(np.mean(final_col >= t))
        prob_statements.append({
            'threshold': round(t, 0),
            'probability': round(prob * 100, 1),
            'label': _format_nok(t),
        })

    return SimulationResult(
        years=years,
        median=[round(v, 0) for v in p50],
        p10=[round(v, 0) for v in p10],
        p90=[round(v, 0) for v in p90],
        p25=[round(v, 0) for v in p25],
        p75=[round(v, 0) for v in p75],
        net_worth_year5=summary_at(5),
        net_worth_year10=summary_at(10),
        net_worth_final=summary_at(n),
        prob_statements=prob_statements,
        current_net_worth=round(current_nw, 0),
    )


def _smart_thresholds(current: float, optimistic_end: float) -> List[float]:
    """Generate 4 meaningful milestones between current NW and optimistic end."""
    low = max(current * 0.5, 0)
    high = optimistic_end
    return [
        low + (high - low) * 0.25,
        low + (high - low) * 0.50,
        low + (high - low) * 0.75,
        high * 0.90,
    ]


def _format_nok(value: float) -> str:
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M NOK"
    return f"{value/1_000:.0f}K NOK"
