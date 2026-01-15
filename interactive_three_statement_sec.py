from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import requests
import pandas as pd

SEC_USER_AGENT = "Andrew Ignatescu (atig@bu.edu)"
SEC_HEADERS = {
    "User-Agent": SEC_USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}

TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json"


@dataclass
class BaseYear:
    year: int
    revenue: float
    cogs: float
    sga: float
    da: float
    interest: float
    tax_rate: float
    net_income: float
    cash: float
    ar: float
    inventory: float
    other_current_assets: float
    ppe_net: float
    other_noncurrent_assets: float
    ap: float
    accrued_liabilities: float
    other_current_liabilities: float
    long_term_debt: float
    other_noncurrent_liabilities: float
    common_equity: float


@dataclass
class Assumptions:
    years: int
    revenue_growth: float
    cogs_pct_rev: float
    sga_pct_rev: float
    da_pct_rev: float
    interest_pct_debt: float
    tax_rate: float
    ar_pct_rev: float
    inv_pct_rev: float
    ap_pct_rev: float
    accrued_pct_rev: float
    capex_pct_rev: float
    target_debt_pct_assets: float


def prompt_str(label: str, default: str) -> str:
    raw = input(f"{label} (default {default}): ").strip()
    return raw if raw else default


def prompt_int(label: str, default: int) -> int:
    raw = input(f"{label} (default {default}): ").strip()
    return int(raw) if raw else default


def prompt_pct(label: str, default: float) -> float:
    raw = input(f"{label} (default {default}): ").strip()
    if not raw:
        return float(default)
    x = float(raw)
    return x / 100.0 if x > 1.0 else x


def _get_json(url: str, headers: Dict[str, str]) -> Dict[str, Any]:
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def ticker_to_cik(ticker: str) -> str:
    data = _get_json(TICKER_MAP_URL, headers={"User-Agent": SEC_USER_AGENT})
    for _, rec in data.items():
        if rec.get("ticker", "").upper() == ticker.upper():
            return f"{int(rec['cik_str']):010d}"
    raise ValueError("Ticker not found")


def fetch_companyfacts(cik10: str) -> Dict[str, Any]:
    return _get_json(COMPANY_FACTS_URL.format(cik10=cik10), headers=SEC_HEADERS)


def pick_latest_annual_usd(facts: Dict[str, Any], tag: str) -> Optional[Tuple[int, float]]:
    try:
        items = facts["facts"]["us-gaap"][tag]["units"]["USD"]
    except KeyError:
        return None
    annual = [x for x in items if x.get("fp") == "FY"]
    if not annual:
        return None
    latest = sorted(annual, key=lambda x: (x.get("end", ""), x.get("filed", "")))[-1]
    year = latest.get("fy") or int(latest.get("end", "0000")[:4])
    return year, float(latest["val"])


def build_base_year_from_sec(ticker: str) -> BaseYear:
    cik10 = ticker_to_cik(ticker)
    facts = fetch_companyfacts(cik10)

    def get(tag):
        out = pick_latest_annual_usd(facts, tag)
        return out[1] if out else 0.0

    revenue = get("Revenues")
    cogs = get("CostOfRevenue")
    sga = get("SellingGeneralAndAdministrativeExpense")
    da = get("DepreciationDepletionAndAmortization")
    interest = get("InterestExpense")
    net_income = get("NetIncomeLoss")

    assets = get("Assets")
    liabilities = get("Liabilities")
    cash = get("CashAndCashEquivalentsAtCarryingValue")
    ar = get("AccountsReceivableNetCurrent")
    inventory = get("InventoryNet")
    ppe = get("PropertyPlantAndEquipmentNet")
    ap = get("AccountsPayableCurrent")
    accrued = get("AccruedLiabilitiesCurrent")
    debt = get("LongTermDebtNoncurrent")
    equity = get("StockholdersEquity") or (assets - liabilities)

    other_assets = max(0.0, assets - (cash + ar + inventory + ppe))
    other_liab = max(0.0, liabilities - (ap + accrued + debt))

    return BaseYear(
        year=pick_latest_annual_usd(facts, "Revenues")[0],
        revenue=revenue,
        cogs=cogs,
        sga=sga,
        da=da,
        interest=interest,
        tax_rate=0.21,
        net_income=net_income,
        cash=cash,
        ar=ar,
        inventory=inventory,
        other_current_assets=other_assets * 0.5,
        ppe_net=ppe,
        other_noncurrent_assets=other_assets * 0.5,
        ap=ap,
        accrued_liabilities=accrued,
        other_current_liabilities=other_liab * 0.5,
        long_term_debt=debt,
        other_noncurrent_liabilities=other_liab * 0.5,
        common_equity=equity,
    )


def forecast(base: BaseYear, a: Assumptions) -> Dict[str, pd.DataFrame]:
    years = [base.year] + [base.year + i for i in range(1, a.years + 1)]

    IS = pd.DataFrame(index=years, columns=["Revenue", "EBIT", "Net Income"])
    BS = pd.DataFrame(index=years, columns=["Cash", "Debt", "Equity", "Assets"])
    CF = pd.DataFrame(index=years, columns=["CFO", "CFI", "CFF", "ΔCash"])

    IS.loc[base.year, ["Revenue", "Net Income"]] = [base.revenue, base.net_income]
    BS.loc[base.year, ["Cash", "Debt", "Equity"]] = [base.cash, base.long_term_debt, base.common_equity]
    BS.loc[base.year, "Assets"] = base.cash + base.ppe_net + base.other_current_assets + base.other_noncurrent_assets

    for y in years[1:]:
        y0 = y - 1
        IS.loc[y, "Revenue"] = IS.loc[y0, "Revenue"] * (1 + a.revenue_growth)
        ebit = IS.loc[y, "Revenue"] * (1 - a.cogs_pct_rev - a.sga_pct_rev - a.da_pct_rev)
        interest = BS.loc[y0, "Debt"] * a.interest_pct_debt
        taxes = max(0, (ebit - interest) * a.tax_rate)
        ni = ebit - interest - taxes

        IS.loc[y, ["EBIT", "Net Income"]] = [ebit, ni]
        BS.loc[y, "Equity"] = BS.loc[y0, "Equity"] + ni
        BS.loc[y, "Debt"] = a.target_debt_pct_assets * BS.loc[y0, "Assets"]

        capex = IS.loc[y, "Revenue"] * a.capex_pct_rev
        CF.loc[y, "CFO"] = ni
        CF.loc[y, "CFI"] = -capex
        CF.loc[y, "CFF"] = BS.loc[y, "Debt"] - BS.loc[y0, "Debt"]
        CF.loc[y, "ΔCash"] = CF.loc[y, ["CFO", "CFI", "CFF"]].sum()

        BS.loc[y, "Cash"] = BS.loc[y0, "Cash"] + CF.loc[y, "ΔCash"]
        BS.loc[y, "Assets"] = BS.loc[y, "Cash"] + BS.loc[y, "Debt"] + BS.loc[y, "Equity"]

    return {"IS": IS.round(2), "BS": BS.round(2), "CF": CF.round(2)}


if __name__ == "__main__":
    ticker = prompt_str("Ticker", "AAPL")
    base = build_base_year_from_sec(ticker)

    years = prompt_int("Forecast years", 5)
    growth = prompt_pct("Revenue growth %", 0.06)

    a = Assumptions(
        years=years,
        revenue_growth=growth,
        cogs_pct_rev=0.60,
        sga_pct_rev=0.20,
        da_pct_rev=0.04,
        interest_pct_debt=0.06,
        tax_rate=0.21,
        ar_pct_rev=0.10,
        inv_pct_rev=0.05,
        ap_pct_rev=0.08,
        accrued_pct_rev=0.04,
        capex_pct_rev=0.05,
        target_debt_pct_assets=0.10,
    )

    out = forecast(base, a)
    for k, v in out.items():
        print(f"\n{k}\n")
        print(v.to_string())

