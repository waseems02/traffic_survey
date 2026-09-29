"""Cleanup loaders for the external-datasets page (page 7).

Each Excel source file is a hand-built pivot table from Excel, not tidy data.
The functions here turn each pivot region into a clean long-form DataFrame
that plotly-express can chart directly.

Every loader returns a `pd.DataFrame`. Missing files return an empty frame
(no exceptions) so the page can render a warning instead of crashing.
"""
from __future__ import annotations

import os
from functools import lru_cache

import pandas as pd

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

FILE_MOJ_BASE = "נתוני בסיס מהבה.xlsx"
FILE_POLICE_COURTS = "דוחות לפי בימש משטרה 19.8.2025.xlsx"
FILE_TRIAL_22_24 = "דוחות במ ובקשות להישפט 2022-2024.xlsx"
FILE_TRIAL_19_21 = "דוחות במ ובקשות להישפט 2019-2021.xlsx"


def _resolve(filename: str) -> str:
    return os.path.join(_PROJECT_ROOT, filename)


def _safe_read(path: str, **kwargs) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_excel(path, **kwargs)
    except Exception:
        return pd.DataFrame()


# =============================================================================
#  File 1 — נתוני בסיס מה"ב  (משרד המשפטים)
# =============================================================================
@lru_cache(maxsize=1)
def load_closure_reasons() -> pd.DataFrame:
    """Case-closure reasons for traffic files (תת"ע) by year.

    Left pivot in File 1, cols 0-4, rows 2-10 (row 11 is the total — dropped).
    Returns long-form: reason | year | count.
    """
    raw = _safe_read(_resolve(FILE_MOJ_BASE), sheet_name="גיליון1", header=None)
    if raw.empty:
        return pd.DataFrame(columns=["reason", "year", "count"])

    block = raw.iloc[2:11, 0:5].copy()
    block.columns = ["reason", 2022, 2023, 2024, 2025]
    block = block.dropna(subset=["reason"])
    long = block.melt(id_vars="reason", var_name="year", value_name="count")
    long["count"] = pd.to_numeric(long["count"], errors="coerce").fillna(0)
    long["year"] = long["year"].astype(int).astype(str)
    long = long[long["count"] > 0]
    return long


@lru_cache(maxsize=1)
def load_process_outcomes() -> pd.DataFrame:
    """Case outcomes (הרשעה, זיכוי, מחיקה, …) by year — grouped into
    the 4 coded categories used in the source pivot's right-hand column.

    Middle pivot in File 1, cols 12-17. Uses the coding in col 17 to group
    detailed outcomes into a smaller set of categories.
    """
    raw = _safe_read(_resolve(FILE_MOJ_BASE), sheet_name="גיליון1", header=None)
    if raw.empty:
        return pd.DataFrame(columns=["category", "year", "count"])

    block = raw.iloc[2:20, [12, 13, 14, 15, 16, 17]].copy()
    block.columns = ["outcome", 2022, 2023, 2024, 2025, "category"]
    block = block.dropna(subset=["outcome", "category"])
    for y in (2022, 2023, 2024, 2025):
        block[y] = pd.to_numeric(block[y], errors="coerce").fillna(0)

    grouped = (
        block.groupby("category")[[2022, 2023, 2024, 2025]]
        .sum()
        .reset_index()
    )
    long = grouped.melt(id_vars="category", var_name="year", value_name="count")
    long["year"] = long["year"].astype(int).astype(str)
    long = long[long["count"] > 0]
    return long


@lru_cache(maxsize=1)
def load_conviction_acquittal_rates() -> pd.DataFrame:
    """Conviction and acquittal rates per year — clean sub-table on the right
    of File 1 (cols 31-34, rows 2-4).

    Returns long: year | metric | pct.
    """
    raw = _safe_read(_resolve(FILE_MOJ_BASE), sheet_name="גיליון1", header=None)
    if raw.empty:
        return pd.DataFrame(columns=["year", "metric", "pct"])

    block = raw.iloc[2:5, [31, 33, 34]].copy()
    block.columns = ["year", "אחוז זיכויים", "אחוז הרשעות"]
    block["year"] = pd.to_numeric(block["year"], errors="coerce").astype("Int64").astype(str)
    for c in ("אחוז זיכויים", "אחוז הרשעות"):
        block[c] = pd.to_numeric(block[c], errors="coerce") * 100

    long = block.melt(id_vars="year", var_name="metric", value_name="pct").dropna()
    return long


# =============================================================================
#  File 2 — דוחות לפי בימ"ש משטרה  (משטרה × בתי משפט)
# =============================================================================
@lru_cache(maxsize=1)
def _raw_police_reports() -> pd.DataFrame:
    df = _safe_read(_resolve(FILE_POLICE_COURTS), sheet_name="גיליון1")
    if df.empty:
        return df
    keep = ["שנה", "סה\"כ דוחות", "בית משפט", "סמל עבירה", "קנס", "נכנס"]
    df = df[[c for c in keep if c in df.columns]].copy()
    df["סה\"כ דוחות"] = pd.to_numeric(df["סה\"כ דוחות"], errors="coerce").fillna(0)
    return df


def load_reports_by_year() -> pd.DataFrame:
    """Total police reports filed to courts, by year (2022-2024). Long: year | total."""
    df = _raw_police_reports()
    if df.empty:
        return pd.DataFrame(columns=["year", "total"])
    out = (
        df.groupby("שנה")["סה\"כ דוחות"].sum()
        .reset_index().rename(columns={"שנה": "year", "סה\"כ דוחות": "total"})
    )
    out["year"] = out["year"].astype(int).astype(str)
    return out


def load_top_courts() -> pd.DataFrame:
    """Top 15 courts by total reports (summed across 2022-2024).
    Long: בית משפט | total.
    """
    df = _raw_police_reports()
    if df.empty:
        return pd.DataFrame(columns=["בית משפט", "total"])
    totals = df.groupby("בית משפט")["סה\"כ דוחות"].sum().nlargest(15)
    out = totals.reset_index().rename(columns={"סה\"כ דוחות": "total"})
    return out


def load_top_offenses() -> pd.DataFrame:
    """Top 15 offense types by report volume (2022-2024). Long: סמל עבירה | total."""
    df = _raw_police_reports()
    if df.empty or "סמל עבירה" not in df.columns:
        return pd.DataFrame(columns=["סמל עבירה", "total"])
    totals = df.groupby("סמל עבירה")["סה\"כ דוחות"].sum().nlargest(15)
    out = totals.reset_index().rename(columns={"סה\"כ דוחות": "total"})
    return out


def load_reports_by_fine() -> pd.DataFrame:
    """Distribution of police reports by fine amount — keeps only the main
    fine tiers (≥ 5,000 reports) so tiny outlier fines don't clutter the chart.

    Long: קנס (label) | total.
    """
    df = _raw_police_reports()
    if df.empty or "קנס" not in df.columns:
        return pd.DataFrame(columns=["קנס", "total"])
    totals = df.groupby("קנס")["סה\"כ דוחות"].sum().reset_index()
    totals = totals.rename(columns={"סה\"כ דוחות": "total"})
    totals = totals[totals["total"] >= 5000].sort_values("קנס")
    totals["קנס"] = totals["קנס"].astype(int).astype(str) + " ₪"
    return totals


def load_reports_entered_by_year() -> pd.DataFrame:
    """Reports that 'entered' the court process vs. didn't, per year.
    Long: year | נכנס | total.
    """
    df = _raw_police_reports()
    if df.empty or "נכנס" not in df.columns:
        return pd.DataFrame(columns=["year", "נכנס", "total"])
    out = (
        df.groupby(["שנה", "נכנס"])["סה\"כ דוחות"].sum()
        .reset_index()
        .rename(columns={"שנה": "year", "סה\"כ דוחות": "total"})
    )
    out["year"] = out["year"].astype(int).astype(str)
    return out


# =============================================================================
#  Files 3 + 4 — בקשות להישפט (2019-2024 combined)
# =============================================================================
@lru_cache(maxsize=1)
def _raw_trial_requests_combined() -> pd.DataFrame:
    """Concatenate the demographic sheets from both files into one 2019-2024
    dataframe with columns: שנה | מין אזרח | דת אזרח | קבוצת גיל | בקשות.
    """
    keep = ["שנה", "מין אזרח", "דת אזרח", "קבוצת גיל בזמן עבירה", "סה\"כ בקשות להישפט"]

    d1 = _safe_read(_resolve(FILE_TRIAL_19_21), sheet_name="בקשות להישפט")
    d2 = _safe_read(_resolve(FILE_TRIAL_22_24), sheet_name="בקשות להישפט דמוגרפי")

    frames = []
    for df in (d1, d2):
        if df.empty:
            continue
        sub = df[[c for c in keep if c in df.columns]].copy()
        sub = sub.dropna(subset=["שנה", "סה\"כ בקשות להישפט"])
        sub["שנה"] = pd.to_numeric(sub["שנה"], errors="coerce").astype("Int64")
        sub["סה\"כ בקשות להישפט"] = pd.to_numeric(sub["סה\"כ בקשות להישפט"], errors="coerce").fillna(0)
        frames.append(sub)

    if not frames:
        return pd.DataFrame(columns=keep)
    return pd.concat(frames, ignore_index=True)


def load_trial_requests_by_year() -> pd.DataFrame:
    """Total trial requests per year, 2019-2024. Long: year | total."""
    df = _raw_trial_requests_combined()
    if df.empty:
        return pd.DataFrame(columns=["year", "total"])
    out = (
        df.groupby("שנה")["סה\"כ בקשות להישפט"].sum()
        .reset_index().rename(columns={"שנה": "year", "סה\"כ בקשות להישפט": "total"})
    )
    out = out.dropna(subset=["year"])
    out["year"] = out["year"].astype(int).astype(str)
    return out


def load_trial_requests_by_religion_gender() -> pd.DataFrame:
    """Trial requests split by religion (x) and gender (color), summed across
    all six years. Excludes 'לא ידוע' rows for readability.
    """
    df = _raw_trial_requests_combined()
    if df.empty:
        return pd.DataFrame(columns=["דת אזרח", "מין אזרח", "total"])
    work = df[(df["דת אזרח"] != "לא ידוע") & (df["מין אזרח"] != "לא ידוע")]
    out = (
        work.groupby(["דת אזרח", "מין אזרח"])["סה\"כ בקשות להישפט"].sum()
        .reset_index().rename(columns={"סה\"כ בקשות להישפט": "total"})
    )
    return out


def load_trial_request_rate_by_fine() -> pd.DataFrame:
    """% of total files that become trial requests, by fine amount (2022-2024).

    Uses the `מפורט` sheet of File 3: aggregates ברירות משפט + בקשות across
    all 3 years per קנס, then computes the ratio.
    """
    df = _safe_read(_resolve(FILE_TRIAL_22_24), sheet_name="מפורט", header=[0, 1])
    if df.empty:
        return pd.DataFrame(columns=["קנס", "אחוז בקשות להישפט", "סך תיקים"])

    fine_col = [c for c in df.columns if c[0] == "קנס"]
    if not fine_col:
        return pd.DataFrame(columns=["קנס", "אחוז בקשות להישפט", "סך תיקים"])
    fine_col = fine_col[0]

    def sum_group(name: str) -> pd.Series:
        cols = [c for c in df.columns if c[0] == name]
        if not cols:
            return pd.Series(dtype=float)
        return df[cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)

    work = pd.DataFrame({
        "קנס": pd.to_numeric(df[fine_col], errors="coerce"),
        "total": sum_group("סה\"כ ברירות משפט"),
        "trial": sum_group("בקשות להישפט"),
    }).dropna(subset=["קנס"])
    work = work[work["קנס"] > 0]

    agg = work.groupby("קנס").agg({"total": "sum", "trial": "sum"}).reset_index()
    agg = agg[agg["total"] >= 500]  # drop tiny buckets so the chart isn't noisy
    agg["אחוז בקשות להישפט"] = (agg["trial"] / agg["total"]) * 100
    agg["קנס"] = agg["קנס"].astype(int).astype(str) + " ₪"
    agg = agg.sort_values("trial", ascending=False)
    return agg.rename(columns={"total": "סך תיקים"})[["קנס", "אחוז בקשות להישפט", "סך תיקים"]]
