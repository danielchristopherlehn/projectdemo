import numpy as np
from dataclasses import dataclass
from typing import List


@dataclass
class SimulationInput:
    property_value: float
    liquid_value: float
    investment_value: float
    total_debt: float
    avg_interest_rate: float
    annual_income: float
    income_growth_rate: float
    horizon: int
    property_drift: float
    property_volatility: float
    investment_drift: float
    investment_volatility: float
    inflation_rate: float
    savings_rate: float
    n_paths: int = 1000


@dataclass
class SimulationResult:
    years: List[int]
    median: List[float]
    p10: List[float]
    p90: List[float]
    p25: List[float]
    p75: List[float]
    net_worth_year5: dict
    net_worth_year10: dict
    net_worth_final: dict
    prob_statements: List[dict]
    current_net_worth: float


def run_simulation(inp: SimulationInput) -> SimulationResult:
    np.random.seed(None)

    dt = 1.0
    n = inp.horizon
    N = inp.n_paths

    mu_prop = inp.property_drift / 100
    sig_prop = inp.property_volatility / 100
    mu_inv = inp.investment_drift / 100
    sig_inv = inp.investment_volatility / 100
    inflation = inp.inflation_rate / 100
    income_g = inp.income_growth_rate / 100
    savings_r = inp.savings_rate / 100

    current_nw = (
        inp.property_value
        + inp.liquid_value
        + inp.investment_value
        - inp.total_debt
    )

    prop_paths = np.zeros((N, n + 1))
    prop_paths[:, 0] = inp.property_value
    prop_noise = np.random.normal(0, 1, (N, n))

    for t in range(1, n + 1):
        prop_paths[:, t] = prop_paths[:, t - 1] * np.exp(
            (mu_prop - 0.5 * sig_prop**2) * dt
            + sig_prop * np.sqrt(dt) * prop_noise[:, t - 1]
        )

    inv_paths = np.zeros((N, n + 1))
    inv_paths[:, 0] = inp.investment_value
    inv_noise = np.random.normal(0, 1, (N, n))

    for t in range(1, n + 1):
        inv_paths[:, t] = inv_paths[:, t - 1] * np.exp(
            (mu_inv - 0.5 * sig_inv**2) * dt
            + sig_inv * np.sqrt(dt) * inv_noise[:, t - 1]
        )

    liquid_paths = np.zeros((N, n + 1))
    liquid_paths[:, 0] = inp.liquid_value

    for t in range(1, n + 1):
        liquid_paths[:, t] = liquid_paths[:, t - 1] * (1 + inflation)

    debt_paths = np.zeros((N, n + 1))
    debt_paths[:, 0] = inp.total_debt

    for t in range(1, n + 1):
        remaining = np.maximum(
            debt_paths[:, t - 1] - debt_paths[:, t - 1] / max(n, 1),
            0
        )
        debt_paths[:, t] = remaining

    annual_income = inp.annual_income

    for t in range(1, n + 1):
        savings = annual_income * savings_r
        liquid_paths[:, t] += savings
        annual_income *= (1 + income_g)

    nw_paths = prop_paths + inv_paths + liquid_paths - debt_paths

    years = list(range(n + 1))
    p10 = np.percentile(nw_paths, 10, axis=0).tolist()
    p25 = np.percentile(nw_paths, 25, axis=0).tolist()
    p50 = np.percentile(nw_paths, 50, axis=0).tolist()
    p75 = np.percentile(nw_paths, 75, axis=0).tolist()
    p90 = np.percentile(nw_paths, 90, axis=0).tolist()

    def summary_at(year):
        if year > n:
            year = n

        col = nw_paths[:, year]

        return {
            "median": round(float(np.percentile(col, 50)), 0),
            "p10": round(float(np.percentile(col, 10)), 0),
            "p90": round(float(np.percentile(col, 90)), 0),
        }

    final_col = nw_paths[:, -1]
    thresholds = _smart_thresholds(current_nw, p90[-1])

    prob_statements = []

    for threshold in thresholds:
        probability = float(np.mean(final_col >= threshold))
        prob_statements.append({
            "threshold": round(threshold, 0),
            "probability": round(probability * 100, 1),
            "label": _format_nok(threshold),
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
        return f"{value / 1_000_000:.1f}M NOK"

    return f"{value / 1_000:.0f}K NOK"