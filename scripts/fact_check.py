"""Fact-check the chickens-vs-people Europe dataset (mechanical checks only).

Runs stages 2-7 of the fact-check process and prints a report. Passing these
quality checks does NOT establish factual accuracy (stage 8 handles that).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "chickens-europe.csv"

RESULT = []  # (status, label, detail)


def report(status: str, label: str, detail: str = "") -> None:
    RESULT.append((status, label, detail))


def main() -> int:
    df = pd.read_csv(CSV)

    # ---- Stage 1: provenance (documented, not computed) ----
    print("=" * 70)
    print("FACT-CHECK REPORT — chickens-europe.csv")
    print("=" * 70)

    # ---- Stage 6: row count vs expected ----
    expected_rows = 41
    report(
        "PASS" if len(df) == expected_rows else "FAIL",
        f"Row count == {expected_rows}",
        f"actual = {len(df)}",
    )

    # ---- Stage 3: types ----
    dtypes = df.dtypes.astype(str).to_dict()
    # pandas 3.x reports string columns as 'str'; pandas 2.x as 'object'. Accept both.
    for col, want in [
        ("country", {"object", "str"}), ("code", {"object", "str"}), ("region", {"object", "str"}),
        ("chickens_millions", {"float64"}), ("people_millions", {"float64"}),
        ("chicken_year", {"int64"}),
    ]:
        got = dtypes.get(col)
        report(
            "PASS" if got in want else "FAIL",
            f"Column '{col}' dtype in {sorted(want)}",
            f"actual = {got}",
        )

    # ---- Stage 3: missing values ----
    for col in df.columns:
        n = int(df[col].isna().sum())
        report("PASS" if n == 0 else "FAIL", f"No missing values in '{col}'", f"missing = {n}")

    # ---- Stage 3: sentinel / impossible values ----
    bad = df[(df["chickens_millions"] <= 0) | (df["people_millions"] <= 0)]
    report(
        "PASS" if bad.empty else "FAIL",
        "chickens_millions and people_millions are positive",
        f"violations = {len(bad)}",
    )

    # ---- Stage 6: duplicate rows / keys ----
    dup_code = df["code"].duplicated().sum()
    dup_name = df["country"].duplicated().sum()
    dup_all = df.duplicated().sum()
    report("PASS" if dup_code == 0 else "FAIL", "Unique ISO code", f"dups = {dup_code}")
    report("PASS" if dup_name == 0 else "FAIL", "Unique country name", f"dups = {dup_name}")
    report("PASS" if dup_all == 0 else "FAIL", "No fully duplicated rows", f"dups = {dup_all}")

    # ---- Stage 5: code format + region category ----
    bad_code = df[~df["code"].str.match(r"^[A-Z]{2}$")]
    report("PASS" if bad_code.empty else "FAIL", "ISO codes are 2 uppercase letters", f"violations = {len(bad_code)}")
    regions = df["region"].value_counts().to_dict()
    report(
        "PASS" if set(regions) <= {"europe", "asia"} else "FAIL",
        "region in {europe, asia}",
        f"values = {regions}",
    )

    # ---- Stage 4: numeric distributions ----
    for col in ["chickens_millions", "people_millions"]:
        s = df[col]
        report("INFO", f"{col} distribution",
               f"min={s.min():.2f} max={s.max():.2f} median={s.median():.2f} mean={s.mean():.2f}")

    df = df.assign(ratio=lambda d: d["chickens_millions"] / d["people_millions"])
    r = df["ratio"]
    report("INFO", "ratio (chickens per person) distribution",
           f"min={r.min():.3f} max={r.max():.3f} median={r.median():.3f} mean={r.mean():.3f}")

    # ---- Stage 4: outliers (IQR on ratio) ----
    q1, q3 = r.quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = df[(r < lo) | (r > hi)].sort_values("ratio", ascending=False)
    report(
        "WARN" if not outliers.empty else "PASS",
        "IQR outlier check on ratio (investigate, not delete)",
        "outliers: " + ", ".join(f"{row.country} {row.ratio:.1f}x" for row in outliers.itertuples()),
    )

    # ---- Stage 2: control totals ----
    eu = df[df["region"] == "europe"]
    tot_c, tot_p = eu["chickens_millions"].sum(), eu["people_millions"].sum()
    report("INFO", "Control total (Europe subset)",
           f"chickens = {tot_c:,.1f}M, people = {tot_p:,.1f}M, overall ratio = {tot_c/tot_p:.2f}x, "
           f"countries = {len(eu)}")

    # ---- Stage 7: logical rule + classification ----
    years = sorted(df["chicken_year"].unique())
    report(
        "PASS" if all(2020 <= y <= 2024 for y in years) else "FAIL",
        "chicken_year within 2020-2024",
        f"values = {years}",
    )

    more = eu[eu["ratio"] > 1]
    fewer = eu[eu["ratio"] <= 1]
    report("INFO", "Classification (Europe): more chickens than people",
           f"{len(more)} of {len(eu)} countries. "
           f"Exceptions: {', '.join(f'{row.country} ({row.ratio:.2f}x)' for row in fewer.sort_values('ratio').itertuples())}")

    # ---- Print ----
    print()
    for status, label, detail in RESULT:
        print(f"[{status:4}] {label}" + (f"  — {detail}" if detail else ""))
    print()

    n_pass = sum(1 for s, _, _ in RESULT if s == "PASS")
    n_fail = sum(1 for s, _, _ in RESULT if s == "FAIL")
    n_warn = sum(1 for s, _, _ in RESULT if s == "WARN")
    print(f"Summary: {n_pass} passed, {n_fail} failed, {n_warn} warnings, "
          f"{len(RESULT)-n_pass-n_fail-n_warn} info.")
    print("\nNOTE: passing quality checks does not establish factual accuracy.")
    print("Stage 8 (source re-verification + independent manual check) is required.")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
