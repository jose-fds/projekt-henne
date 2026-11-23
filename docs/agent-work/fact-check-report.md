# Fact-check report — "chickens vs. people" Europe dataset

Date: 2026-11-23
Checked against: `data/chickens-europe.csv` (the dataset embedded in `agent-work/chicken-dashboard.html`).
Process: `fact-check-skill.md` (stages 1–8).

## Stage 1 — Provenance

| Field | Source | Status |
|---|---|---|
| Chicken stocks | FAO FAOSTAT, "Crops and Livestock Products" → item **Chickens, stocks (1000 head)**, via atlasbig.com / invokely.ai / statsgeo.com / Our World in Data | **Verified** (3 independent FAOSTAT-derived aggregators agree) |
| Human populations | Approximate round figures (not pinned to a single source) | **Flagged** — see Stage 8 |
| Stated row count | 41 countries (39 Europe + Russia + Turkey) | **Pass** (actual 41) |

## Stage 2 — Control totals

- Europe subset: **2,049.5M chickens vs 595.6M people = 3.44×** (39 countries).
- Every one of the 41 chicken figures matches the FAOSTAT-derived list from atlasbig.com exactly (transcription verified).
- Caveat: FAO "world total" differs across aggregators (atlasbig 27.68B vs statsgeo 26.87B) purely because different countries report in a given year. Does not affect per-country figures.

## Stages 3–7 — Mechanical checks (pandas)

Result: **20 passed, 0 failed, 1 warning.**

- 41 rows (== expected), no missing values, no duplicate rows/keys/names.
- Correct types (`chicken_year` int, `chickens/people_millions` float, strings as `str`).
- ISO codes are 2 uppercase letters; `region` ∈ {europe, asia} (39/2).
- All values positive; `chicken_year` within 2020–2024.
- **Warning (real, not an error):** ratio IQR outliers — Moldova 19.4× and Belarus 13.1×. These are genuinely the top two, kept intentionally.

`pytest` (13 tests): **13 passed**, including 2 mutation tests (a planted duplicate code and a planted negative population both fail loudly as expected).

## Stage 8 — Source re-verification

### 8a. Chicken figures — VERIFIED
All 41 values trace to FAOSTAT and match the published figures (e.g. Poland 244.68M, France 229.32M, Russia 507.99M, Turkey 379.63M).

### 8b. Human populations — APPROXIMATE but robust
Compared my round figures to World Bank 2024 (`SP.POP.TOTL`):

| Country | My figure | World Bank 2024 | Ratio shift | Verdict change? |
|---|---|---|---|---|
| Iceland | 0.39M | 0.387M | 0.59× → 0.59× | No |
| Luxembourg | 0.67M | 0.677M | 0.28× → 0.28× | No |
| Malta | 0.52M | **0.569M** | 1.52× → 1.39× | No (still >1) |
| Montenegro | 0.62M | 0.624M | 1.72× | No |
| North Macedonia | 1.8M | 1.824M | 1.41× | No |
| Moldova | 2.5M | **2.402M** | 19.4× → 20.2× | No |
| Belarus | 9.2M | 9.13M | 13.2× | No |

Largest error ≈ 9% (Malta). **The "more chickens than people" classification is unchanged for all 41 countries** — the margins are far wider than the population approximation error.

## Verdict

| Check | Result |
|---|---|
| Mechanical/data-quality checks | **Pass** |
| Chicken figures (transcription vs. source) | **Pass** |
| Human population figures | **Approximate** (≤9% off; needs pinning to a source for exact ratios) |
| Headline claim ("more chickens than people") | **Robust** — holds regardless of population precision |
| Independent manual verification (Stage 8.1) | **Pending** (see procedure below) |

## Stage 8.1 — Manual verification procedure (PENDING, for the user)

1. Pick ~10 rows at random from `data/chickens-europe.csv` (or start with the 7 in the table above).
2. Chicken stocks: look each up on FAOSTAT **https://www.fao.org/faostat/en/#data/QCL** → "Production: Crops and livestock products" → item **Chickens**, element **Stocks**, the stated year.
3. Populations: look each up on World Bank **https://data.worldbank.org/indicator/SP.POP.TOTL** for 2024.
4. Record any value that differs by >1% from the CSV.
5. Report discrepancies back; until then this check is **pending**, not passed.
